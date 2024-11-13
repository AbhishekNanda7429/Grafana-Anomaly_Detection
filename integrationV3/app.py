# app.py

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from anomaly_detection import AnomalyDetectionModel
import pandas as pd
import pickle
import os
import traceback
from datetime import datetime
import boto3
from io import StringIO

app = FastAPI()

# Define request body schema using Pydantic
class ModelParams(BaseModel):
    threshold_multiplier: float
    s3_uri: str  # Accepting S3 bucket URL instead of filepath
    var: str
    bucket_name: str  # New field for specifying S3 bucket name
    s3_folder_path: str = "models"  # Optional parameter with default folder path


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
        model.run_pipeline(bucket_name=params.bucket_name, s3_folder_path=params.s3_folder_path)

        return {"message": f"Model trained and saved for variable '{params.var}' in bucket '{params.bucket_name}/{params.s3_folder_path}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/")
async def predict(
    var: str = Form(...),  # Use Form to specify that `var` comes from form data
    model_folder: str = Form("models"),  # Default to "models" if not provided
    file: UploadFile = File(...)  # Use File to specify file upload
):
    # Load the appropriate model based on var and model_folder
    model_path = os.path.join(model_folder, f"{var}_model.pkl")
    if not os.path.isfile(model_path):
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        # Load the model
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)
        
        # Read the uploaded CSV file into a DataFrame
        data_df = pd.read_csv(file.file)

        # Check if the actual values column is present
        value_column = f"GET /{var}"
        if value_column in data_df.columns:
            # Calculate rolling mean and residual dynamically
            data_df['Rolling_Mean'] = data_df[value_column].rolling(window=10).mean()  # Set appropriate window size
            data_df['Residual'] = data_df[value_column] - data_df['Rolling_Mean']
            data_df.dropna(inplace=True)  # Drop rows with NaN values
        elif "Residual" not in data_df.columns:
            # If neither Residual nor the value column is present, raise an error
            raise HTTPException(
                status_code=400,
                detail=f"CSV file must contain either 'Residual' column or '{value_column}' for predictions"
            )

        # Perform predictions
        predictions = model.predict(data_df[['Residual']])
        anomaly_flags = [1 if pred == -1 else 0 for pred in predictions]  # Map -1 to anomaly, 1 to normal

        # Add predictions to the DataFrame
        data_df["Prediction"] = anomaly_flags

        # Generate a dynamic output filename
        input_filename = file.filename
        output_filename = f"{os.path.splitext(input_filename)[0]}_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_path = os.path.join("output_files", output_filename)

        # Ensure output directory exists
        os.makedirs("output_files", exist_ok=True)
        
        # Save the DataFrame with predictions to a CSV file
        data_df.to_csv(output_path, index=False)

        # Return the path of the saved file
        return {"message": "Prediction completed", "output_file": output_filename}
    except Exception as e:
        # Capture the traceback for more detail
        error_detail = traceback.format_exc()
        print("Error during prediction:", error_detail)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
