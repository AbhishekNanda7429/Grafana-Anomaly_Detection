# prediction_service.py

import os
import pickle
import pandas as pd
import boto3
from datetime import datetime
from fastapi import HTTPException
import traceback
from io import BytesIO
import io
import urllib.parse

class PredictionService:
    def __init__(self, s3_bucket_name, s3_model_prefix, s3_output_prefix):
        self.s3_bucket_name = s3_bucket_name
        self.s3_model_prefix = s3_model_prefix
        self.s3_output_prefix = s3_output_prefix
        # Initialize the S3 client
        self.s3_client = boto3.client('s3')

    def download_file_from_s3(self, s3_uri):
        # Parse the S3 URI
        parsed_uri = urllib.parse.urlparse(s3_uri)
        bucket_name = parsed_uri.netloc
        key = parsed_uri.path.lstrip('/')

        try:
            # Fetch the file from S3
            file_obj = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            file_data = file_obj['Body'].read()
            # print(f"s3 file download is done!!!!!")
            return file_data
        except self.s3_client.exceptions.NoSuchKey:
            raise HTTPException(status_code=404, detail="File not found in S3 bucket")

    def get_model_filename_from_s3_uri(self, s3_uri):
        # Extract the base file name from the S3 URI
        parsed_uri = urllib.parse.urlparse(s3_uri)
        base_filename = os.path.basename(parsed_uri.path)  # Get filename from path
        # Replace special characters like "/" with "_slash_" for safe model filename
        model_filename = base_filename.replace("/", "_slash_").replace(" ", "").replace("_result.csv", "_model.pkl")
        print(f"Model filename derived from S3 URI: {model_filename}")
        return model_filename

    def load_model(self, model_filename):
        # Build the S3 path to the model
        model_key = f"{self.s3_model_prefix}/{model_filename}"
        
        try:
            # Fetch the model from S3
            model_obj = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=model_key)
            model_data = model_obj['Body'].read()
            
            # Load the model using pickle
            model = pickle.load(BytesIO(model_data))
            return model
        except self.s3_client.exceptions.NoSuchKey:
            raise HTTPException(status_code=404, detail=f"Model not found in S3 bucket: {model_key}")

    def prepare_data(self, data_df, value_column):
        # Calculate rolling mean, standard deviation, and residuals
        data_df['Rolling_Mean'] = data_df[value_column].rolling(window=10).mean()
        data_df['Rolling_Std'] = data_df[value_column].rolling(window=10).std()
        data_df['Upper_Bound'] = data_df['Rolling_Mean'] + 3 * data_df['Rolling_Std']
        data_df['Lower_Bound'] = data_df['Rolling_Mean'] - 3 * data_df['Rolling_Std']
        data_df['Residual'] = data_df[value_column] - data_df['Rolling_Mean']
        data_df.dropna(inplace=True)

        return data_df

    def predict(self, data_df, model):
        predictions = model.predict(data_df[['Residual']])
        #Map predictions: -1 (anomaly) -> True, 1 (normal) -> False
        anomaly_flags = [True if pred == -1 else False for pred in predictions]
        data_df["Anomaly"] = anomaly_flags
        return data_df

    def save_predictions(self, data_df, model_filename):
        # Derive the output filename from the model filename
        output_filename = model_filename.replace("_model.pkl", "_prediction.csv")
        
        # Ensure 'Upper_Bound' and 'Lower_Bound' are part of the output CSV
        if 'Upper_Bound' not in data_df.columns or 'Lower_Bound' not in data_df.columns:
            raise HTTPException(
                status_code=500,
                detail="Upper_Bound and Lower_Bound not found in DataFrame. Ensure they are calculated before saving."
            )
        
        # Convert the DataFrame to CSV in memory
        csv_buffer = io.StringIO()
        data_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Go to the beginning of the in-memory file

        # Create the S3 key for the output file in the outputs folder
        output_key = f"{self.s3_output_prefix}/{output_filename}"

        # Upload the CSV file to the S3 bucket in the outputs folder
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key=output_key,
                Body=csv_buffer.getvalue(),
                ContentType='text/csv'
            )
            print(f"the output csv file name:", output_filename)
            return output_filename
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload predictions to S3: {str(e)}")

    def run_prediction_pipeline(self, s3_uri):
        try:
            # Download the file from S3 URI
            file_data = self.download_file_from_s3(s3_uri)
            data_df = pd.read_csv(io.BytesIO(file_data))  # Read CSV from bytes
            # print(f"till here done!!!!!!!!!!!!!!!!!!!!!!!!!")
            
            # Get the model filename from the input CSV URI
            model_filename = self.get_model_filename_from_s3_uri(s3_uri)
            
            # Load the model from S3
            model = self.load_model(model_filename)
            
            # Process the data and make predictions
            value_column = data_df.columns[1]  # The target column, assuming it's the second column
            data_df = self.prepare_data(data_df, value_column)
            data_df = self.predict(data_df, model)
            
            # Save the predictions back to S3 (in the "outputs" folder)
            output_filename = self.save_predictions(data_df, model_filename)
            return {"message": "Prediction completed", "output_file": output_filename}
        except Exception as e:
            error_detail = traceback.format_exc()
            print("Error during prediction:", error_detail)
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
