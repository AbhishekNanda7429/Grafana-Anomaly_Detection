# app.py

import os
from fastapi import FastAPI, HTTPException,Form
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from GrafanaDataFetcher.requestcall import PrometheusDashboardClient
from GrafanaDataFetcher.grafana_data_fetcher import GrafanaDataFetcher
from anomaly_detection import AnomalyDetectionModel
from prediction_service import PredictionService
from GrafanaDataFetcher.grafana_data_processor import GrafanaDataProcessor
from apscheduler.schedulers.background import BackgroundScheduler
# Initialize FastAPI app
app = FastAPI()

# Read environment variables
from dotenv import load_dotenv
load_dotenv()


S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_MODEL_PREFIX = os.getenv("S3_MODEL_PREFIX")
# S3_OUTPUT_PREFIX = os.getenv("S3_OUTPUT_PREFIX")

# Initialize PredictionService with S3 parameters
prediction_service = PredictionService(
    s3_bucket_name=S3_BUCKET_NAME,
    s3_model_prefix=S3_MODEL_PREFIX,
    # s3_output_prefix=S3_OUTPUT_PREFIX
)

# Input schema for the API request
class FetchDashboardDataRequest(BaseModel):
    username: str
    password: str
    dashboard_uid: str
    timeframe: List[str]  # Two timestamps: start and end

#api to extract data, train data and save the data
@app.post("/extract_train_save/")
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
                for col, df in clean_data.items():
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

def predict_cron_job():
    base_url = "https://op.cloudbuilders.io"
    username = 'admin'
    password = 'Imfine123$'
    dashboard_uid = "opentelemetry-apm"
    output_dir = "grafana-anomaly/data"

    # UTC offset in seconds
    utc_offset_seconds = 19800  # 5 hours 30 minutes

    # Calculate dynamic timeframe: last 15 minutes
    # Adjust current UTC time by the offset
    end_time = datetime.utcnow() 
    
    start_time = end_time - timedelta(minutes=100)
    timeframe = [start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')]
    print(f"Adjusted Timeframe (with UTC Offset): {timeframe}")

    # Instantiate and run the processor
    processor = GrafanaDataProcessor(base_url, username, password, dashboard_uid, output_dir)
    try:
        processor.run(timeframe)
        print(f"Prediction completed successfully for timeframe {timeframe}")
    except Exception as e:
        print(f"Prediction failed: {str(e)}")

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(predict_cron_job, "interval", minutes=100)
scheduler.start()

# Endpoint to trigger the cron job manually (optional)
@app.post("/predict_cron/")
async def predict_cron():
    predict_cron_job()
    return {"status": "success", "message": "Prediction triggered manually."}

# Ensure the scheduler shuts down properly on app termination
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()