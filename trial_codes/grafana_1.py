import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Grafana API details
GRAFANA_URL = "https://op.cloudbuilders.io"
API_KEY = "glsa_Y8WYTAWLM3BoHHDGYSUb86e59kbGkBIw_523e9ead"
DASHBOARD_UID = "opentelemetry-apm"
PROMETHEUS_URL = "http://3.82.60.81:9090"

# Define the time range for the query
start_time_str = "2024-01-01 18:43:01"  # Start date
end_time_str = "2024-08-23 18:43:02"  # End date

# Convert the human-readable dates to Unix timestamps (seconds since the epoch)
start_time = int(time.mktime(datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S").timetuple()))
end_time = int(time.mktime(datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S").timetuple()))


# Set up the headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Get the dashboard JSON configuration
dashboard_url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
response = requests.get(dashboard_url, headers=headers)
dashboard_data = response.json()

# Function to query Prometheus
def query_prometheus(query, start_time, end_time):
    prometheus_query_url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {
        'query': query,
        'start': start_time,
        'end': end_time,
        'step': '12000s'  # Query data at a 1-minute interval, adjust as needed
    }
    response = requests.get(prometheus_query_url, params=params)
    return response.json()

# Loop through all panels in the dashboard and query Prometheus
for panel in dashboard_data['dashboard']['panels']:
    panel_id = panel['id']
    panel_title = panel.get('title', 'Unnamed Panel')
    
    print(f"\nPanel ID: {panel_id}")
    print(f"Panel Title: {panel_title}")
    
    for target in panel.get('targets', []):
        prom_query = target.get('expr', None)
        if prom_query:
            print(f"Querying Prometheus with: {prom_query}")
            
            # Query Prometheus
            data = query_prometheus(prom_query, start_time, end_time)
            
            # Print the raw data
            print(data)