# # app.py

# import os
# from fastapi import FastAPI, HTTPException, Form
# from pydantic import BaseModel
# from anomaly_detection import AnomalyDetectionModel
# from prediction_service import PredictionService
# import pandas as pd
# from datetime import datetime
# import boto3
# from io import StringIO
# import io
# from dotenv import load_dotenv
# from GrafanaDataFetcher.requestcall import PrometheusDashboardClient
# from GrafanaDataFetcher.grafana_data_fetcher import GrafanaDataFetcher
# from typing import List
# from pathlib import Path
# app = FastAPI()

# # Load environment variables from the .env file
# load_dotenv()

# # Read from environment variables
# S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
# S3_MODEL_PREFIX = os.getenv("S3_MODEL_PREFIX")
# S3_OUTPUT_PREFIX = os.getenv("S3_OUTPUT_PREFIX")

# # Initialize PredictionService with S3 parameters
# prediction_service = PredictionService(
#     s3_bucket_name=S3_BUCKET_NAME,
#     s3_model_prefix=S3_MODEL_PREFIX,
#     s3_output_prefix=S3_OUTPUT_PREFIX
# )

# # Input schema for the API request
# class FetchDashboardDataRequest(BaseModel):
#     username: str
#     password: str
#     dashboard_uid: str
#     timeframe: List[str]  # Two timestamps: start and end

# # Define request body schema using Pydantic
# class ModelParams(BaseModel):
#     threshold_multiplier: float
#     s3_uri: str  # Accepting S3 bucket URL 

# #to download files from s3 bucket
# def download_from_s3(s3_uri):
#     s3 = boto3.client('s3')
#     bucket_name = s3_uri.split('/')[2]
#     key = '/'.join(s3_uri.split('/')[3:])
    
#     csv_obj = s3.get_object(Bucket=bucket_name, Key=key)
#     body = csv_obj['Body'].read().decode('utf-8')
#     return pd.read_csv(StringIO(body))

# @app.post("/fetch_dashboard_data/")
# async def fetch_dashboard_data(request: FetchDashboardDataRequest):
#     """
#     Fetch and process data from Grafana/Prometheus based on the given parameters.
#     """
#     try:
       
#         # Initialize Prometheus client
#         client = PrometheusDashboardClient(request.username, request.password)
        
#         # Fetch dashboard data
#         dashboard_data = client.get_queries_and_service_data(request.dashboard_uid, request.timeframe)
#         if not dashboard_data:
#             raise HTTPException(status_code=404, detail="No data found for the specified dashboard UID and timeframe.")
        
#         # Extract data
#         service_names = dashboard_data.get("service_names", [])
#         http_routes = dashboard_data.get("http_routes", [])
#         prometheus_datasource_uid = dashboard_data.get("prometheus_datasource_uid")
#         data_source = {"type": "prometheus", "uid": prometheus_datasource_uid}

#         output_dir = Path("grafana-anomaly/data")
#         output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        
#         result = {}  # Store results for all services

#         for service_name in service_names:
#             # Initialize Grafana data fetcher
#             data_fetcher = GrafanaDataFetcher(
#                 "https://op.cloudbuilders.io",
#                 request.username,
#                 request.password,
#                 service_name,
#                 http_routes,
#                 data_source
#             )

#             # Fetch and process data
#             data = data_fetcher.fetch_data(request.timeframe)
#             dataframes = data_fetcher.parse_frames_to_dataframes(data)
#             result_df = data_fetcher.merge_dataframes(dataframes)

#             # Clean data
#             clean_data = data_fetcher.process_and_clean_data(result_df)

#             # Save cleaned data and prepare result
#             service_results = {}
#             if clean_data:
#                 for col, df in clean_data.items():
#                     output_file = output_dir / f"{service_name}_{col.replace(' ', '_').replace('/', '_')}_result.csv"
#                     # # Save to file
#                     data_fetcher.save_dataframe(df, output_file)
#                     # # Convert to JSON for returning in response
#                     service_results[col] = df.to_dict(orient="records")
                    
#             else:
#                 service_results["error"] = f"No data to save for {service_name}"
            
#             result[service_name] = service_results

#         return {"status": "success", "data": clean_data}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching or processing data: {str(e)}")

# #trains the model with new data before doing prediction
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

#         # Return a success message
#         return {"message": "Model trained and saved successfully. You can now use /predict for predictions."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/predict/")
# async def predict(
#     s3_uri: str = Form(...),
# ):
#     try:
#         # Download the most recent CSV data from S3 URI
#         file_data = prediction_service.download_file_from_s3(s3_uri)
#         data_df = pd.read_csv(io.BytesIO(file_data))  # Read CSV from bytes
        
#         # Get the sanitized model filename and target column
#         model_filename, value_column = prediction_service.get_sanitized_model_filename(data_df)
        
#         # Overwrite the model with the new data (retrain and overwrite the same model)
#         model_params = ModelParams(threshold_multiplier=3.5, s3_uri=s3_uri)
        
#         # Call the /train_model endpoint, which will handle training
#         train_result = await train_model(model_params)
        
#         # Once training is done, perform prediction with the newly trained model
#         result = prediction_service.run_prediction_pipeline(s3_uri)
        
#         # Return the prediction results
#         return {
#             "message": "Model trained and prediction completed successfully.",
#             "training_result": train_result["message"],
#             "prediction_result": result
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

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

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List
from GrafanaDataFetcher.requestcall import PrometheusDashboardClient
from GrafanaDataFetcher.grafana_data_fetcher import GrafanaDataFetcher
from anomaly_detection import AnomalyDetectionModel

# Initialize FastAPI app
app = FastAPI()

# Read environment variables
from dotenv import load_dotenv
load_dotenv()

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_MODEL_PREFIX = os.getenv("S3_MODEL_PREFIX")

# Input schema for the API request
class FetchDashboardDataRequest(BaseModel):
    username: str
    password: str
    dashboard_uid: str
    timeframe: List[str]  # Two timestamps: start and end


@app.post("/full_pipeline/")
async def full_pipeline(request: FetchDashboardDataRequest):
    """
    Complete pipeline: Fetch data, train models for each CSV file, and save them to S3.
    """
    try:
        # Step 1: Fetch data from Grafana/Prometheus
        output_dir = Path("grafana-anomaly/data")
        output_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        
        # Initialize Prometheus client
        client = PrometheusDashboardClient(request.username, request.password)
        dashboard_data = client.get_queries_and_service_data(request.dashboard_uid, request.timeframe)

        if not dashboard_data:
            raise HTTPException(status_code=404, detail="No data found for the specified dashboard UID and timeframe.")

        service_names = dashboard_data.get("service_names", [])
        http_routes = dashboard_data.get("http_routes", [])
        prometheus_datasource_uid = dashboard_data.get("prometheus_datasource_uid")
        data_source = {"type": "prometheus", "uid": prometheus_datasource_uid}

        # Initialize results storage
        training_results = {}

        for service_name in service_names:
            # Fetch and process data
            data_fetcher = GrafanaDataFetcher(
                "https://op.cloudbuilders.io",
                request.username,
                request.password,
                service_name,
                http_routes,
                data_source
            )

            data = data_fetcher.fetch_data(request.timeframe)
            dataframes = data_fetcher.parse_frames_to_dataframes(data)
            result_df = data_fetcher.merge_dataframes(dataframes)
            clean_data = data_fetcher.process_and_clean_data(result_df)

            if clean_data:
                # for col, df in clean_data.items():
                #     # Save the clean data locally
                #     output_file = output_dir / f"{service_name}_{col.replace(' ', '_').replace('/', '_')}_result.csv"
                #     data_fetcher.save_dataframe(df, output_file)
                for col, df in clean_data.items():
                    # output_file = output_dir / f"{service_name.replace('-', '')}_{col.replace(' ', '_').replace('/', '_slash_')}_result.csv"
                    output_file = output_dir / f"{service_name.replace('-', '')}_{col.replace(' ', '_').replace('/', '_slash_').replace('*', '_star_')}_result.csv"
                    print(f"Saving data to {output_file} for service_name {service_name}")
                    data_fetcher.save_dataframe(df, output_file)
                    # print(df)

                    # Train the model
                    try:
                        model = AnomalyDetectionModel(
                            threshold_multiplier=3.5,  # Example threshold
                            data=df,
                            csv_filename=output_file.name  # Pass the name of the input CSV file
                        )
                        # Generate model filename based on CSV filename
                        model_filename = output_file.name.replace("_result.csv", "_model.pkl")
                        s3_model_path = f"{S3_MODEL_PREFIX}/{model_filename}"

                        # Run the pipeline
                        model.run_pipeline(bucket_name=S3_BUCKET_NAME, s3_folder_path=S3_MODEL_PREFIX)

                        # Save result for this model
                        training_results[output_file.name] = {
                            "status": "success",
                            "model_s3_path": s3_model_path
                        }
                    except Exception as e:
                        training_results[output_file.name] = {
                            "status": "failure",
                            "error": str(e)
                        }
            else:
                training_results[service_name] = {"status": "failure", "error": "No clean data available."}

        return {"status": "success", "training_results": training_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

