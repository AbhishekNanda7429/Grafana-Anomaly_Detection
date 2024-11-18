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
import io
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
    s3_uri: str  # Accepting S3 bucket URL 

def download_from_s3(s3_uri):
    s3 = boto3.client('s3')
    bucket_name = s3_uri.split('/')[2]
    key = '/'.join(s3_uri.split('/')[3:])
    
    csv_obj = s3.get_object(Bucket=bucket_name, Key=key)
    body = csv_obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(body))

#trains the model with new data before doing prediction
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

        # Return a success message
        return {"message": "Model trained and saved successfully. You can now use /predict for predictions."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/")
async def predict(
    s3_uri: str = Form(...),
):
    try:
        # Download the most recent CSV data from S3 URI
        file_data = prediction_service.download_file_from_s3(s3_uri)
        data_df = pd.read_csv(io.BytesIO(file_data))  # Read CSV from bytes
        
        # Get the sanitized model filename and target column
        model_filename, value_column = prediction_service.get_sanitized_model_filename(data_df)
        
        # Overwrite the model with the new data (retrain and overwrite the same model)
        model_params = ModelParams(threshold_multiplier=3.5, s3_uri=s3_uri)
        
        # Call the /train_model endpoint, which will handle training
        train_result = await train_model(model_params)
        
        # Once training is done, perform prediction with the newly trained model
        result = prediction_service.run_prediction_pipeline(s3_uri)
        
        # Return the prediction results
        return {
            "message": "Model trained and prediction completed successfully.",
            "training_result": train_result["message"],
            "prediction_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

#==============================

#base code- runs the routes separately
# @app.post("/train_model/")
# async def train_model(params: ModelParams):
#     # Download the CSV data from S3 URL
#     try:
#         data = download_from_s3(params.s3_uri)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to download file from S3: {str(e)}")
    
#     # Initialize and run the model pipeline
#     try:
#         model = AnomalyDetectionModel(
#             threshold_multiplier=params.threshold_multiplier,
#             data=data
#         )
#         # Run the pipeline, specifying the bucket and S3 path for saving the model
#         model.run_pipeline(bucket_name=S3_BUCKET_NAME, s3_folder_path=S3_MODEL_PREFIX)

#         return {"message": "Model trained and saved successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/predict/")
# async def predict(
#     s3_uri: str = Form(...)
# ):
#     # Run the prediction pipeline and return the result
#     try:
#         # Run the prediction pipeline directly using the S3 URI
#         result = prediction_service.run_prediction_pipeline(s3_uri)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

#=============================

#if the model is not available, then asks to run /train_model first
# @app.post("/train_model/")
# async def train_model(params: ModelParams):
#     # Download the CSV data from S3 URL
#     try:
#         data = download_from_s3(params.s3_uri)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to download file from S3: {str(e)}")
    
#     # Initialize and run the model pipeline
#     try:
#         model = AnomalyDetectionModel(
#             threshold_multiplier=params.threshold_multiplier,
#             data=data
#         )
#         # Run the pipeline, specifying the bucket and S3 path for saving the model
#         model.run_pipeline(bucket_name=S3_BUCKET_NAME, s3_folder_path=S3_MODEL_PREFIX)

#         return {"message": "Model trained and saved successfully."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/predict/")
# async def predict(
#     s3_uri: str = Form(...),
# ):
#     try:
#         # Download the file from S3 URI
#         file_data = prediction_service.download_file_from_s3(s3_uri)
#         data_df = pd.read_csv(io.BytesIO(file_data))  # Read CSV from bytes
        
#         # Get the sanitized model filename and target column
#         model_filename = prediction_service.get_sanitized_model_filename(data_df)
        
#         # Check if the model exists in the S3 bucket
#         model_key = f"{S3_MODEL_PREFIX}/{model_filename}"
#         try:
#             # Try fetching the model object to check existence
#             prediction_service.s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=model_key)
#         except prediction_service.s3_client.exceptions.ClientError as e:
#             # If the model is not found, return an error message
#             if e.response['Error']['Code'] == "404":
#                 return {
#                     "message": f"Model not found in S3: {model_key}. Please train the model first by calling /train_model."
#                 }
#             else:
#                 # Other errors
#                 raise HTTPException(status_code=500, detail=f"Error checking model existence: {str(e)}")
        
#         # Proceed with prediction as the model exists
#         result = prediction_service.run_prediction_pipeline(s3_uri)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

#==============================

