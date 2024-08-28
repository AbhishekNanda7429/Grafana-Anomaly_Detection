import json
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt
from datetime import datetime

class GrafanaPrometheusDataFetcher:
    def __init__(self, url, username, password, query_url):
        self.url = url
        self.username = username
        self.password = password
        self.query_url = query_url
        
    def fetch_data(self, body):
        """Fetches data from the Prometheus API."""
        try:
            response = requests.post(self.query_url, auth=HTTPBasicAuth(self.username, self.password), json=body)
            response.raise_for_status()
            print("Data retrieved successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve data: {e}")
            return None
    
    def process_data(self, data, ref_id='A'):
        """Processes the JSON data and converts it into a Pandas DataFrame."""
        metrics = []
        for frame in data['results'][ref_id]['frames']:
            labels = frame['schema']['fields'][1]['labels']
            times = frame['data']['values'][0]
            values = frame['data']['values'][1]
            for t, v in zip(times, values):
                metrics.append({'Time': t, 'Value': v, **labels})
        df = pd.DataFrame(metrics)
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        return df
    
    def plot_data(self, df, expr):
        """Plots the data from the DataFrame."""
        plt.figure(figsize=(10, 6))
        plt.plot(df['Time'], df['Value'], label=f'{expr} Rate', color='blue')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title(f'Time Series of {expr} Rate')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def build_query_body(self, expr, from_time, to_time, queries_type, uid):
        """Builds the query body for fetching data."""
        return {
            "queries": [
                {
                    "refId": "A",
                    "expr": f"rate({expr}[$__rate_interval])",
                    "range": True,
                    "datasource": {"type": queries_type, "uid": uid},
                    "intervalMs": 15000,
                    "maxDataPoints": 1539
                },
                {
                    "refId": "A-Instant",
                    "expr": f"rate({expr}[$__rate_interval])",
                    "instant": True,
                    "datasource": {"type": queries_type, "uid": uid},
                    "intervalMs": 15000,
                    "maxDataPoints": 1539
                }
            ],
            "from": from_time,
            "to": to_time
        }
    
    def get_resources(self, path):
        """Fetches available resources from the Prometheus API."""
        try:
            response = requests.get(f"{self.url}{path}", auth=HTTPBasicAuth(self.username, self.password))
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve resources: {e}")
            return []
    
    @staticmethod
    def convert_to_timestamp(date_str):
        """Converts a date string to a Unix timestamp in milliseconds."""
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return str(int(dt.timestamp() * 1000))

# # Example usage:
# if __name__ == "__main__":
#     url = 'https://op.cloudbuilders.io'
#     username = 'admin'
#     password = 'Imfine123$'
#     timeframes = ['2024-08-22 13:06:55', '2024-08-22 14:06:55']
#     query_url = f"{url}/api/ds/query?ds_type=prometheus&requestId=explore_x25"
    
#     fetcher = GrafanaPrometheusDataFetcher(url, username, password, query_url)
#     from_time = fetcher.convert_to_timestamp(timeframes[0])
#     to_time = fetcher.convert_to_timestamp(timeframes[1])
    
#     queries_type = "prometheus"
#     uid = "dds0jxfdwvo5cb"
    
#     path = "/api/datasources/uid/dds0jxfdwvo5cb/resources/api/v1/label/__name__/values"
#     expr_list = fetcher.get_resources(path=f"{path}?start={from_time}&end={to_time}")
    
#     main_df = {}
    
#     for expr in expr_list:
#         body = fetcher.build_query_body(expr, from_time, to_time, queries_type, uid)
#         json_data = fetcher.fetch_data(body)
        
#         if json_data:
#             # Process both 'A' and 'A-Instant' data
#             for ref_id in ['A', 'A-Instant']:
#                 if ref_id in json_data['results']:
#                     df = fetcher.process_data(json_data, ref_id)
                    
#                     # Plot data
#                     fetcher.plot_data(df, expr)
                    
#                     # Store DataFrame in main_df
#                     if expr not in main_df:
#                         main_df[expr] = {}
#                     main_df[expr][ref_id] = df
    
#     print(main_df)
