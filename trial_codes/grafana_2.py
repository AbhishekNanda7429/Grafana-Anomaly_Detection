import requests
import json

# Prometheus server URL
prometheus_url = "http://3.82.60.81:9090"

# Define the query you want to execute
query = 'up{job="prometheus"}'  # Example: Get status of all instances of a specific job

# Build the full query URL
query_url = f"{prometheus_url}/api/v1/query"

# Send the GET request to Prometheus
response = requests.get(query_url, params={'query': query})

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    print (data)

    # Check if the response contains data
    if data['status'] == 'success':
        results = data['data']['result']
        for result in results:
            metric = result['metric']
            value = result['value']
            print(f"Metric: {metric}, Value: {value}")
    else:
        print("Query failed: ", data['status'])
else:
    print("Failed to connect to Prometheus, status code:", response.status_code)
