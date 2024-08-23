# import requests
# import json

# # Prometheus details
# prometheus_url = "http://3.82.60.81:9090/"
# query1 = "sum(duration_milliseconds_count{span_kind=\"SPAN_KIND_SERVER\", service_name=\"$app\", http_route=~\"$route\"}) by(service_name)"  # Replace with your actual Prometheus query
# query2 = "sum(duration_milliseconds_count{span_kind=\"SPAN_KIND_SERVER\", service_name=\"$app\", http_route=~\"$route\"}) by(span_name)"
# query= "http_requests_total"
# # Specify the time range
# from_time = "2023-08-23T12:54:36Z"  # Start date in ISO format
# to_time = "2023-08-23T13:09:13Z"    # End date in ISO format

# # API endpoint for querying Prometheus
# query_url = f"{prometheus_url}/api/v1/query_range"

# # Parameters for the query
# params = {
#     "query": query,
#     "start": from_time,
#     "end": to_time,
#     "step": "30s"  # Adjust the step interval if needed
# }

# # Make the request to Prometheus
# response = requests.get(query_url, params=params)

# # Check if the request was successful
# if response.status_code == 200:
#     data = response.json()
#     if data['data']['result']:
#         print("Data from Prometheus:")
#         print(json.dumps(data, indent=2))
#     else:
#         print("No data found for the specified query and time range.")
# else:
#     print(f"Failed to retrieve data: {response.status_code} - {response.text}")
#-------------------------------------------------------------------------------------

import requests
import datetime

# Replace with your Prometheus server URL
PROMETHEUS_URL = "http://3.82.60.81:9090"

# Define your Prometheus query (for example, getting the `up` metric)
query = 'sort_desc(duration_milliseconds_sum{span_kind="SPAN_KIND_SERVER", service_name="$app", http_status_code!="", http_route=~"$route"} / duration_milliseconds_count{span_kind="SPAN_KIND_SERVER", service_name="$app", http_status_code!="", http_route=~"$route"})'

# Define the time range
start_time = "2024-08-01T00:00:00Z"  # ISO format (UTC)
end_time = "2024-08-22T23:59:59Z"    # ISO format (UTC)

# Define the step (e.g., 60s for 1 minute intervals)
step = "60s"

# Prepare the API request
params = {
    'query': query,
    'start': start_time,
    'end': end_time,
    'step': step
}

try:
    # Make the request to the Prometheus API
    response = requests.get(PROMETHEUS_URL, params=params)
    
    # Check the status code
    if response.status_code == 200:
        try:
            # Attempt to parse the response as JSON
            data = response.json()
            print("Successfully retrieved data:")
            print(data)
        except requests.exceptions.JSONDecodeError:
            # If the response is not valid JSON
            print("Failed to decode JSON. Here's the raw response:")
            print(response.text)
    else:
        print(f"Failed to query Prometheus. Status code: {response.status_code}")
        print("Response text:")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")