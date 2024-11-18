from numpy import result_type
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import json

class PrometheusDashboardClient:
    def __init__(self, username, password, base_url="https://op.cloudbuilders.io/api"):
        
        self.username = username
        self.password = password
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password)
        self.headers = {'Content-Type': 'application/json'}

    def fetch_dashboard_data(self, dashboard_uid):
        """Fetches dashboard data by UID."""
        url = f"{self.base_url}/dashboards/uid/{dashboard_uid}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def extract_datasource_uid_and_queries(self, data):
        """Extracts Prometheus datasource UID and queries from dashboard data."""
        datasource_uid = None
        queries = []
        for panel in data['dashboard']['panels']:
            for target in panel.get('targets', []):
                if target['datasource']['type'] == 'prometheus':
                    datasource_uid = target['datasource']['uid']
                    queries.append(target['expr'])
        return datasource_uid, queries

    def convert_timeframe_to_unix(self, timeframe):
        """Converts a list of datetime strings to Unix timestamps in milliseconds."""
        return [int(datetime.strptime(time, '%Y-%m-%d %H:%M:%S').timestamp()) for time in timeframe]

    def fetch_service_names(self, datasource_uid, start_time, end_time):
        """Fetches service names for a specific datasource UID within a timeframe."""
        url = f"{self.base_url}/datasources/uid/{datasource_uid}/resources/api/v1/label/service_name/values?start={start_time}&end={end_time}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def fetch_http_routes(self, datasource_uid, start_time, end_time):
        """Fetches HTTP routes for a specific datasource UID within a timeframe."""
        url = f"{self.base_url}/datasources/uid/{datasource_uid}/resources/api/v1/label/http_route/values?start={start_time}&end={end_time}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_queries_and_service_data(self, dashboard_uid, timeframe):
        """Fetches and returns data including queries, service names, and HTTP routes."""
        # Step 1: Fetch Dashboard Data
        data = self.fetch_dashboard_data(dashboard_uid)
        
        # Step 2: Extract Prometheus Datasource UID and Queries
        datasource_uid, queries = self.extract_datasource_uid_and_queries(data)
        
        # Step 3: Convert Timeframe to Unix Timestamps
        converted_timeframe = self.convert_timeframe_to_unix(timeframe)
        
        # Step 4: Fetch Service Names
        service_names = self.fetch_service_names(datasource_uid, converted_timeframe[0], converted_timeframe[1])
        
        # Step 5: Fetch HTTP Routes
        http_routes = self.fetch_http_routes(datasource_uid, converted_timeframe[0], converted_timeframe[1])
        
        # Organize the data into a dictionary

        result={
            "prometheus_datasource_uid": datasource_uid,
            "queries": queries,
            "service_names": service_names.get("data", []),
            "http_routes": http_routes.get("data", [])
        }
        
        return result

# # Instantiate and use the class
# if __name__ == "__main__":
#     # Credentials and timeframe
#     username = 'admin'
#     password = 'Imfine123$'
#     dashboard_uid = "opentelemetry-apm"
#     timeframe = ['2024-11-07 17:32:00', '2024-11-08 00:44:00']

#     # Initialize client
#     client = PrometheusDashboardClient(username, password)
#     # Fetch data and store in a variable
#     dashboard_data = client.get_queries_and_service_data(dashboard_uid, timeframe)
    
#     # Display the result
#     print(json.dumps(dashboard_data, indent=4))
