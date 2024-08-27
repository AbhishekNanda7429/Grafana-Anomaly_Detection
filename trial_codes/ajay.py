import json
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt 
from datetime import datetime

class PrometheusDataFetcher:
    def __init__(self, url, username, password, query_url):
        """
        Initializes the PrometheusDataFetcher with necessary credentials.
        """
        self.url = url
        self.username = username
        self.password = password
        self.query_url = query_url
        
    def fetch_data(self, body):
        """
        Fetches data from the Prometheus API using the provided query body.
        
        :param body: The query body for the Prometheus API request.
        :return: The JSON response data or None if the request fails.
        """
        try:
            response = requests.post(self.query_url, auth=HTTPBasicAuth(self.username, self.password), json=body)
            response.raise_for_status()  # Raises an error for bad HTTP responses
            print("Data retrieved successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def process_data(self, data, ref_id):
        """
        Processes the JSON data and converts it into a Pandas DataFrame.
        
        :param data: JSON data from Prometheus API.
        :param ref_id: The reference ID in the query ('A' or 'A-Instant').
        :return: Pandas DataFrame with processed data.
        """
        metrics = []
        
        for frame in data['results'][ref_id]['frames']:
            # Extract labels (e.g., route, status code)
            labels = frame['schema']['fields'][1].get('labels', {})
            
            # Extract time and value data
            times = frame['data']['values'][0]
            values = frame['data']['values'][1]
            
            # Append each time-value pair with associated labels to the metrics list
            for t, v in zip(times, values):
                metrics.append({
                    'Time': t,
                    'Value': v,
                    **labels  # Add all the labels as columns
                })

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(metrics)
        
        # Convert 'Time' from Unix timestamp to datetime
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        
        return df
    
    def plot_data(self, df, expr, ref_id):
        """
        Plots the data from the DataFrame.
        
        :param df: DataFrame containing the data to be plotted.
        :param expr: The expression used in the Prometheus query (used for labeling).
        :param ref_id: The reference ID in the query ('A' or 'A-Instant') used for plot titles.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(df['Time'], df['Value'], label=f'{expr} ({ref_id})', color='blue')
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title(f'Time Series of {expr} Rate ({ref_id})')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def build_query_body(self, expr, from_time, to_time):
        """
        Builds the query body for fetching data from Prometheus.
        
        :param expr: Prometheus expression to query.
        :param from_time: Start time for the query.
        :param to_time: End time for the query.
        :return: The query body as a dictionary.
        """
        return  {
            "queries": [
                {
                    "refId": "A",
                    "expr": f"rate({expr}[$__rate_interval])",
                    "range": True,
                    "instant": False,
                    "datasource": {
                        "type": "prometheus",
                        "uid": "dds0jxfdwvo5cb"
                    },
                    "editorMode": "builder",
                    "legendFormat": "__auto",
                    "useBackend": False,
                    "disableTextWrap": False,
                    "fullMetaSearch": False,
                    "includeNullMetadata": True,
                    "exemplar": False,
                    "requestId": "40449A",
                    "utcOffsetSec": 19800,
                    "interval": "",
                    "datasourceId": 3,
                    "intervalMs": 15000,
                    "maxDataPoints": 1539
                },
                {
                    "refId": "A-Instant",
                    "expr": f"rate({expr}[$__rate_interval])",
                    "range": False,
                    "instant": True,
                    "datasource": {
                        "type": "prometheus",
                        "uid": "dds0jxfdwvo5cb"
                    },
                    "editorMode": "builder",
                    "legendFormat": "__auto",
                    "useBackend": False,
                    "disableTextWrap": False,
                    "fullMetaSearch": False,
                    "includeNullMetadata": True,
                    "exemplar": False,
                    "requestId": "40449A",
                    "utcOffsetSec": 19800,
                    "interval": "",
                    "datasourceId": 3,
                    "intervalMs": 15000,
                    "maxDataPoints": 1539
                }
            ],
            "from": from_time,
            "to": to_time
        }
    
    def get_resources(self, path):
        """
        Fetches resources from a given API path.
        
        :param path: API endpoint path to get resources from.
        :return: The list of resource names.
        """
        try:
            response = requests.get(f"{self.url}{path}", auth=HTTPBasicAuth(self.username, self.password))
            response.raise_for_status()  # Raises an error for bad HTTP responses
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching resources: {e}")
            return []
    
    @staticmethod
    def convert_to_timestamp(date_str):
        """
        Converts a date string to a Unix timestamp in milliseconds.
        
        :param date_str: Date string in the format 'YYYY-MM-DD HH:MM:SS'.
        :return: The corresponding Unix timestamp in milliseconds as a string.
        """
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        timestamp = int(dt.timestamp() * 1000)  # Convert to milliseconds
        print(f"Converted {date_str} to timestamp: {timestamp}")
        return str(timestamp)

# Example usage:
if __name__ == "__main__":
    # URL and credentials for the Prometheus API
    url = 'https://op.cloudbuilders.io'
    username = 'admin'
    password = 'Imfine123$'
    
    # Define timeframes for the query
    timeframes = ['2024-08-20 13:06:55', '2024-08-22 14:06:55']
    query_url = f"{url}/api/ds/query?ds_type=prometheus&requestId=explore_x25"
    
    # Initialize PrometheusDataFetcher
    fetcher = PrometheusDataFetcher(url, username, password, query_url)
    
    # Convert the timeframes to timestamps
    from_time = fetcher.convert_to_timestamp(timeframes[0])
    to_time = fetcher.convert_to_timestamp(timeframes[1])
    
    # Define API path to get resource names (Prometheus metric names)
    path = "/api/datasources/uid/dds0jxfdwvo5cb/resources/api/v1/label/__name__/values?start=1724389980&end=1724393640"
    
    # Fetch resource names (metric names)
    expr_list = fetcher.get_resources(path=path)
    
    # Loop through each metric and process its data
    for expr in expr_list:
        body = fetcher.build_query_body(expr, from_time, to_time)
        
        # Fetch data from the API
        json_data = fetcher.fetch_data(body)
        
        if json_data:
            # Process and plot data for both "A" and "A-Instant"
            for ref_id in ["A", "A-Instant"]:
                if ref_id in json_data['results']:
                    df = fetcher.process_data(json_data, ref_id)
                    print(df)
                    # fetcher.plot_data(df, expr, ref_id)
            
            # Optionally print the DataFrame for debugging purposes