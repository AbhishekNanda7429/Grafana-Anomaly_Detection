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
start_time_str = "1970-01-01 18:43:01"  # Start date
end_time_str = "2024-08-23 18:43:02"  # End date

# # Convert times to Prometheus-compatible format (Unix timestamp)
# start_timestamp = int(start_time.timestamp())
# end_timestamp = int(end_time.timestamp())

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
def query_prometheus(query, start, end):
    prometheus_query_url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {
        'query': query,
        'start': "1724416473032",
        'end': "1724420073032",
        'step': '600s'  # Query data at a 1-minute interval, adjust as needed
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

            # # Process and convert the data into a pandas DataFrame
            # results = []
            # for result in data['data']['result']:
            #     for value in result['values']:
            #         timestamp, metric_value = value
            #         results.append([datetime.fromtimestamp(float(timestamp)), float(metric_value)])
            
            # df = pd.DataFrame(results, columns=['timestamp', 'value'])
            
            # # Output the DataFrame
            # print(df.head())  # Print first few rows
            # # You can save the DataFrame to a CSV or use it in your ML model
            # df.to_csv(f'panel_{panel_id}_{panel_title}.csv', index=False)

#--------------------------------------------------
# # Step 1: Get the dashboard JSON configuration
# dashboard_url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
# response = requests.get(dashboard_url, headers=headers)
# dashboard_data = response.json()

# # Extract the panel data (assuming you're querying a specific panel)
# # Panel queries are usually stored in the "panels" key of the dashboard JSON
# for panel in dashboard_data['dashboard']['panels']:
#     if panel['id'] == int(PANEL_ID):
#         panel_query = panel['targets']  # Extract the query for the data source
#         # This part depends on the data source, modify the query to your needs

# # Step 2: Query the data source directly (e.g., Prometheus, InfluxDB, Elasticsearch)
# # This step requires you to know the specifics of the data source.
# # For example, if you're querying Prometheus:

# PROMETHEUS_QUERY = "sum(duration_milliseconds_count{span_kind=\"SPAN_KIND_SERVER\", service_name=\"$app\", http_route=~\"$route\"}) by(span_name)"

# prometheus_url = f"{GRAFANA_URL}/api/datasources/proxy/{panel['datasource']['id']}/api/v1/query"
# params = {'query': PROMETHEUS_QUERY}
# response = requests.get(prometheus_url, headers=headers, params=params)
# data = response.json()

# # Convert the data to a pandas DataFrame
# df = pd.DataFrame(data['data']['result'])

# # Step 3: Process the DataFrame (e.g., feature engineering, normalization)
# # Assuming you have time-series data, this will depend on your use case
# df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')  # Example processing

# # Step 4: Feed the DataFrame into a machine learning model
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier

# # Example: Preprocessing your data
# X = df.drop(columns=['target_column'])
# y = df['target_column']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# # Example ML model: Random Forest
# model = RandomForestClassifier()
# model.fit(X_train, y_train)

# # Evaluate the model
# accuracy = model.score(X_test, y_test)
# print(f"Model Accuracy: {accuracy}")