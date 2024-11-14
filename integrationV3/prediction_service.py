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

    def load_model(self, var):
        # Build the S3 path to the model
        model_key = f"{self.s3_model_prefix}/{var}_model.pkl"
        
        try:
            # Fetch the model from S3
            model_obj = self.s3_client.get_object(Bucket=self.s3_bucket_name, Key=model_key)
            model_data = model_obj['Body'].read()
            
            # Load the model using pickle
            model = pickle.load(BytesIO(model_data))
            return model
        except self.s3_client.exceptions.NoSuchKey:
            raise HTTPException(status_code=404, detail="Model not found in S3 bucket")

    def download_file_from_s3(self, s3_uri):
        # Parse the S3 URI
        parsed_uri = urllib.parse.urlparse(s3_uri)
        bucket_name = parsed_uri.netloc
        key = parsed_uri.path.lstrip('/')

        try:
            # Fetch the file from S3
            file_obj = self.s3_client.get_object(Bucket=bucket_name, Key=key)
            file_data = file_obj['Body'].read()
            return file_data
        except self.s3_client.exceptions.NoSuchKey:
            raise HTTPException(status_code=404, detail="File not found in S3 bucket")

    def prepare_data(self, data_df, var):
        value_column = f"GET /{var}"
        if value_column in data_df.columns:
            data_df['Rolling_Mean'] = data_df[value_column].rolling(window=10).mean()
            data_df['Residual'] = data_df[value_column] - data_df['Rolling_Mean']
            data_df.dropna(inplace=True)
        elif "Residual" not in data_df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"CSV file must contain either 'Residual' column or '{value_column}' for predictions"
            )
        return data_df

    def predict(self, data_df, model):
        predictions = model.predict(data_df[['Residual']])
        anomaly_flags = [1 if pred == -1 else 0 for pred in predictions]
        data_df["Prediction"] = anomaly_flags
        return data_df

    def save_predictions(self, data_df, var):
        # Prepare the output filename with the model name (var)
        output_filename = f"{var}_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
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
            return output_filename
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload predictions to S3: {str(e)}")

    def run_prediction_pipeline(self, s3_uri, var):
        try:
            # Download the file from S3 URI
            file_data = self.download_file_from_s3(s3_uri)
            data_df = pd.read_csv(io.BytesIO(file_data))  # Read CSV from bytes
            
            # Load the model from S3
            model = self.load_model(var)
            
            # Process the data and make predictions
            data_df = self.prepare_data(data_df, var)
            data_df = self.predict(data_df, model)
            
            # Save the predictions back to S3 (in the "outputs" folder)
            output_filename = self.save_predictions(data_df, var)
            return {"message": "Prediction completed", "output_file": output_filename}
        except Exception as e:
            error_detail = traceback.format_exc()
            print("Error during prediction:", error_detail)
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
