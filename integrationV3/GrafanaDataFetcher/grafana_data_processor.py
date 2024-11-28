#grafana_data_processor

from http import server
from GrafanaDataFetcher.requestcall import PrometheusDashboardClient
from GrafanaDataFetcher.grafana_data_fetcher import GrafanaDataFetcher

from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from ML_model.prediction_service import PredictionService
import os 
from DataInjection.data_injection import S3DataInjector




class GrafanaDataProcessor:
    def __init__(self, base_url, username, password, dashboard_uid, output_dir,athena_database,s3_bucket_name):
        """
        Initialize the GrafanaDataProcessor with credentials and configuration.
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.dashboard_uid = dashboard_uid
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.prometheus_datasource_uid = None
        self.service_names = []
        self.http_routes = []
        self.timeframe = []
        S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
        S3_MODEL_PREFIX = os.getenv("S3_MODEL_PREFIX")
        self.athena_database= athena_database
        self.s3_bucket_name=s3_bucket_name
        # S3_OUTPUT_PREFIX = os.getenv("S3_OUTPUT_PREFIX")

        # Initialize PredictionService with S3 parameters
        self.prediction_service = PredictionService(
            s3_bucket_name=S3_BUCKET_NAME,
            s3_model_prefix=S3_MODEL_PREFIX,
            # s3_output_prefix=S3_OUTPUT_PREFIX
        )



    def fetch_dashboard_data(self, timeframe):
        """
        Fetch dashboard data and populate class variables for further processing.
        """
        self.timeframe = timeframe
        client = PrometheusDashboardClient(self.username, self.password)
        dashboard_data = client.get_queries_and_service_data(self.dashboard_uid, timeframe)
        self.service_names = dashboard_data.get("service_names", [])
        self.http_routes = dashboard_data.get("http_routes", [])
        print(f"Service Names: {self.service_names}", f"HTTP Routes: {self.http_routes}")
        self.prometheus_datasource_uid = dashboard_data.get("prometheus_datasource_uid")

    def process_service_data(self, service_name):
        """
        Fetch, process, and save data for a specific service.
        """
        try:
            data_source = {"type": "prometheus", "uid": self.prometheus_datasource_uid}
            data_fetcher = GrafanaDataFetcher(self.base_url, self.username, self.password, service_name, self.http_routes, data_source,MIN_INTERVAL_MS=15000)
            
            # Fetch and process data
            data = data_fetcher.fetch_data(self.timeframe)
            dataframes = data_fetcher.parse_frames_to_dataframes(data)
            result_df = data_fetcher.merge_dataframes(dataframes)
            print(f"Results for {service_name}:")
            print(result_df)

            # Clean and save data
            clean_data = data_fetcher.process_and_clean_data(result_df)
            if not clean_data:
                print(f"No data to save for {service_name}")
            else:
                for col, df in clean_data.items():
                    # model_name = self.output_dir / f"{service_name.replace('-', '')}_{col.replace(' ', '_').replace('/', '_slash_').replace('*', '_star_')}_result.csv"
                    # print(f"Saving data to {output_file} for service_name {service_name}")
                    # data_fetcher.save_dataframe(df, output_file)
                    
                    model_filename = f"{service_name.replace('-', '')}_{col.replace(' ', '_').replace('/', '_slash_').replace('*', '_star_')}_model.pkl"
                    
                    # print(f"Saving data to {output_file} for service_name {service_name}")
                    # data_fetcher.save_dataframe(df, output_file)
                    ##############anomaly detection code here
                    print(f"there is the model filename:", model_filename)
                    try:
                        anomaly_df = self.prediction_service.run_prediction_pipeline(df, model_filename)

                        print("anomaly data: \n", anomaly_df)
                        # s3_bucket_name = "anomaly-detection-bucket-cloudbuilders"  # env
                        # athena_database = "athena_database"  # env
                        athena_database=self.athena_database
                        s3_bucket_name=self.s3_bucket_name
                        table_name = f"{service_name.replace('-', '')}_{col.replace(' ', '_').replace('/', '_slash_').replace('*', '_star_')}"

                        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID_ATHENA")
                        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY_ATHENA")

                        injector = S3DataInjector(
                            s3_bucket_name, athena_database, aws_access_key_id, aws_secret_access_key, partition_granularity="minute"
                        )
                        result_df = injector.inject_data(anomaly_df, table_name)
                        print(result_df)
                        print("Data injection complete.")
                    except Exception as e:
                        print(f"Error during anomaly detection and data injection for {service_name}: {e}")
                   

        except Exception as e:
            print("anomaly data: /n",anomaly_df)
            print(f"Error processing data for {service_name}: {e}")

    def process_all_services(self):
        """
        Process all services concurrently.
        """
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.process_service_data, service_name): service_name
                for service_name in self.service_names
            }

            for future in as_completed(futures):
                service_name = futures[future]
                try:
                    future.result()  # Ensures we capture exceptions here
                    print(f"Successfully processed data for {service_name}")
                except Exception as e:
                    print(f"Error processing data for {service_name}: {e}")

    def run(self, timeframe):
        """
        Run the entire data processing workflow.
        """
        print("Fetching dashboard data...")
        self.fetch_dashboard_data(timeframe)
        print("Processing all services...")
        self.process_all_services()
        print("Data fetching and processing complete.")


# if __name__ == "__main__":
#     # Configuration
#     base_url = "https://op.cloudbuilders.io"
#     username = 'admin'
#     password = 'Imfine123$'
#     dashboard_uid = "opentelemetry-apm"
#     output_dir = "grafana-anomaly/data"
#     timeframe = ['2024-11-01 10:00:00', '2024-11-14 00:00:00']

#     # Instantiate and run the processor
#     processor = GrafanaDataProcessor(base_url, username, password, dashboard_uid, output_dir)
#     processor.run(timeframe)
