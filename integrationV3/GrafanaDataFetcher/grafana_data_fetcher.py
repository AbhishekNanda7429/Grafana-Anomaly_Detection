import re
import os
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from GrafanaDataFetcher.Nan_value_treatment import DataCleaner


class GrafanaDataFetcher:
    def __init__(self, url, username, password, service_name, http_routes, data_source):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {'Content-Type': 'application/json'}
        self.service_name = service_name
        self.http_routes = http_routes
        self.data_source = data_source

    @staticmethod
    def convert_to_timestamp(date_str):
        """Converts a date string to a Unix timestamp in milliseconds."""
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return str(int(dt.timestamp() * 1000))

    @staticmethod
    def calculate_dynamic_values(timeframe):
        """Calculate intervalMs and maxDataPoints based on the timeframe duration."""
        from_timestamp = GrafanaDataFetcher.convert_to_timestamp(timeframe[0])
        to_timestamp = GrafanaDataFetcher.convert_to_timestamp(timeframe[1])
        duration_seconds = (int(to_timestamp) - int(from_timestamp)) / 1000

        return from_timestamp, to_timestamp, 60000, 50000

    @staticmethod
    def custom_escape(route):
        """Escape special characters in http_routes for Prometheus regex patterns."""
        escaped_route = re.sub(r'([/{}*])', r'\\\1', route)
        return escaped_route.replace("\\", "\\\\")

    def build_query_expression(self):
        """Construct the Prometheus query expression."""
        http_route_pattern = "|".join(self.custom_escape(route) for route in self.http_routes)
        expr = (
            f"""histogram_quantile(0.95, sum(rate(duration_milliseconds_bucket{{"""
            f"""span_kind="SPAN_KIND_SERVER", service_name="{self.service_name}", http_route=~"({http_route_pattern})"}}[3m]))"""
            f""" by (le, span_name))"""
        )
        return expr

    def build_query_body(self, timeframe):
        """Construct the query body for the Grafana API request."""
        from_timestamp, to_timestamp, interval_ms, max_data_points = self.calculate_dynamic_values(timeframe)
        expr = self.build_query_expression()

        return {
            "queries": [
                {
                    "datasource": {
                        "type": self.data_source["type"],
                        "uid": self.data_source["uid"],
                    },
                    "editorMode": "code",
                    "expr": expr,
                    "instant": False,
                    "legendFormat": "{{label_name}}",
                    "range": True,
                    "refId": "A",
                    "exemplar": False,
                    "requestId": "5A",
                    "utcOffsetSec": 19800,
                    "interval": "",
                    "datasourceId": 5,
                    "intervalMs": interval_ms,
                    "maxDataPoints": max_data_points,
                }
            ],
            "from": from_timestamp,
            "to": to_timestamp,
        }

    def fetch_data(self, timeframe):
        """Send request to the Grafana API and fetch data."""
        body = self.build_query_body(timeframe)
        response = requests.post(
            f"{self.url}/api/ds/query?ds_type={self.data_source['type']}",
            headers=self.headers,
            json=body,
            auth=self.auth,
        )
        return response.json()

    @staticmethod
    def parse_frames_to_dataframes(data):
        """Parse the API response and convert frames into DataFrames."""
        dataframes = []
        for frame in data['results']['A']['frames']:
            if len(frame['data']['values']) < 2:
                continue
            time_values = frame['data']['values'][0]
            value_series = frame['data']['values'][1]
            span_name = frame['schema']['fields'][1]['labels']['span_name']
            df = pd.DataFrame({
                'Time': pd.to_datetime(time_values, unit='ms'),
                span_name: value_series,
            })
            dataframes.append(df)
        return dataframes

    @staticmethod
    def merge_dataframes(dataframes):
        """Merge all DataFrames on the 'Time' column."""
        if not dataframes:
            return pd.DataFrame()  # Return an empty DataFrame if no dataframes to merge
        result_df = dataframes[0]
        for df in dataframes[1:]:
            result_df = result_df.merge(df, on='Time', how='outer')
        return result_df

    @staticmethod
    def save_dataframe(df, output_path):
        """Save a DataFrame to a CSV file."""
        os.makedirs(output_path.parent, exist_ok=True)
        df.to_csv(output_path, index=False)

    def process_and_clean_data(self, result_df):
        """Process and deep clean individual columns."""
        cleaned_dataframes = {}
        for col in result_df.columns:
            if col != 'Time':
                df_selected = result_df[['Time', col]]
                cleaned_df = DataCleaner(df_selected).clean_data()
                if not cleaned_df.empty:
                    cleaned_dataframes[col] = cleaned_df
        return cleaned_dataframes


# Example Usage
# if __name__ == "__main__":
#     # Configuration
#     url = "https://op.cloudbuilders.io"
#     username = "admin"
#     password = "Imfine123$"
#     service_name = "spring-boot"
#     http_routes = [
#         "/",
#         "/**",
#         "/chain",
#         "/cpu_task",
#         "/error_test",
#         "/io_task",
#         "/items/{item_id}",
#         "/random_sleep",
#         "/random_status",
#     ]
#     data_source = {"type": "prometheus", "uid": "ddwd6amxd8oowf"}
#     timeframe_3_days = ["2024-11-08 17:32:00", "2024-11-11 17:32:00"]

#     # Create GrafanaDataFetcher instance
#     fetcher = GrafanaDataFetcher(url, username, password, service_name, http_routes, data_source)

#     # Fetch and process data
#     data = fetcher.fetch_data(timeframe_3_days)
#     dataframes = fetcher.parse_frames_to_dataframes(data)
#     result_df = fetcher.merge_dataframes(dataframes)
#     print(result_df)
#     # Save results
#     output_dir = Path("grafana-anomley/data")
#     fetcher.save_dataframe(result_df, output_dir / "result.csv")
#     fetcher.process_and_save_data(result_df)
