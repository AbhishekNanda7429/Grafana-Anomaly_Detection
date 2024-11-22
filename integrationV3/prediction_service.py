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

import os
import pickle
import pandas as pd
from fastapi import HTTPException
import traceback
from io import BytesIO

class PredictionService:
    def __init__(self, s3_bucket_name, s3_model_prefix):
        self.s3_bucket_name = s3_bucket_name
        self.s3_model_prefix = s3_model_prefix
        # S3 client can still be used if needed, though not saving predictions anymore
        self.s3_client = boto3.client('s3')

    def load_model(self, model_filename):
        """
        Load the model from S3 using the provided model filename.
        """
        model_key = f"{self.s3_model_prefix}/{model_filename}"
        print(f"model key:", model_key)
        
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
        """
        Prepare the input data for prediction by calculating rolling mean, std deviation, and residuals.
        """
        data_df['Rolling_Mean'] = data_df[value_column].rolling(window=10).mean()
        data_df['Rolling_Std'] = data_df[value_column].rolling(window=10).std()
        data_df['Upper_Bound'] = data_df['Rolling_Mean'] + 3 * data_df['Rolling_Std']
        data_df['Lower_Bound'] = data_df['Rolling_Mean'] - 3 * data_df['Rolling_Std']
        data_df['Residual'] = data_df[value_column] - data_df['Rolling_Mean']
        data_df.dropna(inplace=True)

        return data_df

    def predict(self, data_df, model):
        """
        Use the loaded model to make predictions on the prepared data.
        """
        predictions = model.predict(data_df[['Residual']])
        # Map predictions: -1 (anomaly) -> True, 1 (normal) -> False
        anomaly_flags = [True if pred == -1 else False for pred in predictions]
        data_df["Anomaly"] = anomaly_flags
        return data_df

    def run_prediction_pipeline(self, data_df, model_filename):
        """
        Run the full prediction pipeline using the provided data and model filename.
        Return the DataFrame with predictions.
        """
        try:
            # Load the model from S3
            model = self.load_model(model_filename)
            
            # Process the data and make predictions
            value_column = data_df.columns[1]  # The target column, assuming it's the second column
            data_df = self.prepare_data(data_df, value_column)
            data_df = self.predict(data_df, model)
            
            return data_df
        except Exception as e:
            error_detail = traceback.format_exc()
            print("Error during prediction:", error_detail)
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
