# app.py

import os
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from anomaly_detection import AnomalyDetectionModel
from prediction_service import PredictionService
import pandas as pd
from datetime import datetime
import boto3
from io import StringIO
from dotenv import load_dotenv  # Import dotenv to load .env variables

app = FastAPI()

# Load environment variables from the .env file
load_dotenv()

# Read from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")  # default value can be set if variable is not found
S3_MODEL_PREFIX = os.getenv("S3_MODEL_PREFIX")
S3_OUTPUT_PREFIX = os.getenv("S3_OUTPUT_PREFIX")

# Initialize PredictionService with S3 parameters
prediction_service = PredictionService(s3_bucket_name=S3_BUCKET_NAME, s3_model_prefix=S3_MODEL_PREFIX,  s3_output_prefix=S3_OUTPUT_PREFIX)

# Define request body schema using Pydantic
class ModelParams(BaseModel):
    threshold_multiplier: float
    s3_uri: str  # Accepting S3 bucket URL instead of filepath
    var: str
    # bucket_name: str  # New field for specifying S3 bucket name
    # s3_folder_path: str = "models"  # Optional parameter with default folder path

class PredictionParams(BaseModel):
    var: str
    model_folder: str = "models"  # Optional, defaults to "models"

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
            data=data,
            var=params.var
        )
        # Run the pipeline, specifying the bucket and S3 path for saving the model
        model.run_pipeline(bucket_name=S3_BUCKET_NAME, s3_folder_path=S3_MODEL_PREFIX)

        return {"message": f"Model trained and saved for variable '{params.var}' in bucket '{S3_BUCKET_NAME}/{S3_MODEL_PREFIX}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/")
async def predict(
    var: str = Form(...),
    s3_uri: str = Form(...)
):
    # Run the prediction pipeline and return the result
    result = prediction_service.run_prediction_pipeline(s3_uri, var)
    return result
