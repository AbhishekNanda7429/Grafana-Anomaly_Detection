# app.py

import os
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from anomaly_detection import AnomalyDetectionModel
from prediction_service import PredictionService
import pandas as pd
from datetime import datetime
import boto3
from io import StringIO
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from the .env file
load_dotenv()

# Read from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_MODEL_PREFIX = os.getenv("S3_MODEL_PREFIX")
S3_OUTPUT_PREFIX = os.getenv("S3_OUTPUT_PREFIX")

# Initialize PredictionService with S3 parameters
prediction_service = PredictionService(
    s3_bucket_name=S3_BUCKET_NAME,
    s3_model_prefix=S3_MODEL_PREFIX,
    s3_output_prefix=S3_OUTPUT_PREFIX
)

# Define request body schema using Pydantic
class ModelParams(BaseModel):
    threshold_multiplier: float
    s3_uri: str  # Accepting S3 bucket URL instead of filepath

def download_from_s3(s3_uri):
    s3 = boto3.client('s3')
    bucket_name = s3_uri.split('/')[2]
    key = '/'.join(s3_uri.split('/')[3:])
    
    csv_obj = s3.get_object(Bucket=bucket_name, Key=key)
    body = csv_obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(body))

@app.post("/train_model/")
async def train_model(params: ModelParams):
    # Download the CSV data from S3 URL
    try:
        data = download_from_s3(params.s3_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file from S3: {str(e)}")
    
    # Initialize and run the model pipeline
    try:
        model = AnomalyDetectionModel(
            threshold_multiplier=params.threshold_multiplier,
            data=data
        )
        # Run the pipeline, specifying the bucket and S3 path for saving the model
        model.run_pipeline(bucket_name=S3_BUCKET_NAME, s3_folder_path=S3_MODEL_PREFIX)

        return {"message": "Model trained and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/")
async def predict(
    s3_uri: str = Form(...)
):
    # Run the prediction pipeline and return the result
    try:
        # Run the prediction pipeline directly using the S3 URI
        result = prediction_service.run_prediction_pipeline(s3_uri)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
