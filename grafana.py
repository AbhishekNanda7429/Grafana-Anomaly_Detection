# import requests
# from requests.auth import HTTPBasicAuth

# GRAFANA_URL = "https://op.cloudbuilders.io"
# username = 'admin'
# password = 'Imfine123$'
# # API_KEY = "your-api-key"

# # headers = {
# #     "Authorization": f"Bearer {API_KEY}",
# #     "Content-Type": "application/json"
# # }

# # Get all dashboards
# response = requests.get(f"{GRAFANA_URL}/api/search",auth=HTTPBasicAuth(username, password) )
# dashboards = response.json()

# # Fetch details for each dashboard
# for dashboard in dashboards:
#     uid = dashboard['uid']
#     response = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", auth=HTTPBasicAuth(username, password))
#     dashboard_data = response.json()
#     # Process dashboard_data as needed
#     print(f"Dashboard: {dashboard['title']}")
#     # You can now access panels, queries, etc. from dashboard_data
#------------------------------------------------------
# import requests
# import json
# from datetime import datetime, timedelta
# from requests.auth import HTTPBasicAuth

# GRAFANA_URL = "https://op.cloudbuilders.io"
# username = 'admin'
# password = 'Imfine123$'

# # headers = {
# #     "Authorization": f"Bearer {API_KEY}",
# #     "Content-Type": "application/json"
# # }

# def get_panel_data(panel, datasource, time_range):
#     # This function will need to be adapted based on your specific data source
#     # This example assumes a Prometheus-like query structure
#     query = panel.get('targets', [{}])[0].get('expr', '')
#     if not query:
#         return None

#     params = {
#         'query': query,
#         'start': time_range['from'],
#         'end': time_range['to'],
#         'step': '60s'  # adjust as needed
#     }

#     response = requests.get(f"{GRAFANA_URL}/api/datasources/proxy/{datasource['id']}/api/v1/query_range", 
#                             auth=HTTPBasicAuth(username, password), params=params)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data for panel {panel['title']}: {response.status_code}")
#         return None

# # Get all dashboards
# response = requests.get(f"{GRAFANA_URL}/api/search", auth=HTTPBasicAuth(username, password))
# dashboards = response.json()

# # Set time range for data queries (last 24 hours)
# now = datetime.now()
# time_range = {
#     'from': (now - timedelta(hours=24)).isoformat(),
#     'to': now.isoformat()
# }
# # Fetch details for each dashboard
# for dashboard in dashboards:
#     uid = dashboard['uid']
#     response = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", auth=HTTPBasicAuth(username, password))
#     dashboard_data = response.json()
    
#     print(f"\nDashboard: {dashboard['title']}")
    
#     # Check if 'dashboard' key exists
#     if 'dashboard' not in dashboard_data:
#         print(f"  Error: 'dashboard' key not found in the response for {dashboard['title']}")
#         print(f"  Response keys: {list(dashboard_data.keys())}")
#         continue
    
#     # Get the actual dashboard content
#     dashboard_content = dashboard_data['dashboard']
    
#     # Check if 'panels' key exists
#     if 'panels' not in dashboard_content:
#         print(f"  Note: 'panels' key not found in dashboard {dashboard['title']}")
#         print(f"  Dashboard keys: {list(dashboard_content.keys())}")
        
#         # Check if the dashboard uses rows
#         if 'rows' in dashboard_content:
#             print("  This dashboard uses rows. Processing row panels...")
#             panels = [panel for row in dashboard_content['rows'] for panel in row.get('panels', [])]
#         else:
#             print("  Unable to find panels or rows in this dashboard.")
#             continue
#     else:
#         panels = dashboard_content['panels']
    
#     # Get datasource info
#     datasource_response = requests.get(f"{GRAFANA_URL}/api/datasources", auth=HTTPBasicAuth(username, password))
#     datasources = {ds['name']: ds for ds in datasource_response.json()}
    
#     # Process each panel
#     for panel in panels:
#         print(f"\n  Panel: {panel['title']}")
        
#         # ... (rest of the code remains the same)
#------------------------------------------------------------------------

# import requests
# from requests.auth import HTTPBasicAuth

# # Grafana details
# grafana_url = "https://op.cloudbuilders.io"
# #api_key = "<your-api-key>"  # You need an API key with the necessary permissions
# username = 'admin'
# password = 'Imfine123$'
# dashboard_uid = "opentelemetry-apm"

# # API endpoint to get the dashboard
# url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"

# # Set the headers including the authorization token
# # headers = {
# #     "Authorization": f"Bearer {api_key}",
# #     "Content-Type": "application/json"
# # }

# # Make the request
# response = requests.get(url, auth=HTTPBasicAuth(username, password))

# # Check if the request was successful
# if response.status_code == 200:
#     dashboard_data = response.json()
#     print(dashboard_data)
# else:
#     print(f"Failed to retrieve dashboard: {response.status_code} - {response.text}")
#----------------------------------------------------------------------------------------------

# import requests
# import json

# # Grafana details
# grafana_url = "https://op.cloudbuilders.io"
# username = 'admin'
# password = 'Imfine123$'
# dashboard_uid = "opentelemetry-apm"

# # Specify the time range (example: last 24 hours)
# from_time = "2023-08-22T00:00:00Z"  # Start date in ISO format
# to_time = "2023-08-23T00:00:00Z"    # End date in ISO format

# # API endpoint to get the dashboard
# url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"

# # Make the request with basic authentication
# response = requests.get(url, auth=(username, password))

# # Check if the request was successful
# if response.status_code == 200:
#     dashboard_data = response.json()
    
#     # Assuming you want to get data from a panel, iterate over panels
#     for panel in dashboard_data['dashboard']['panels']:
#         panel_id = panel['id']
        
#         # URL to query the data for a specific panel
#         panel_query_url = f"{grafana_url}/api/ds/query"
        
#         # Payload for the data query (adjust according to your data source)
#         payload = {
#             "queries": [
#                 {
#                     "panelId": panel_id,
#                     "range": {
#                         "from": from_time,
#                         "to": to_time
#                     },
#                     "intervalMs": 60000,  # Interval in milliseconds (adjust if needed)
#                     "maxDataPoints": 10000,  # Maximum number of data points to return
#                 }
#             ]
#         }
        
#         headers = {
#             "Content-Type": "application/json"
#         }
        
#         # Request data from the panel
#         panel_response = requests.post(panel_query_url, auth=(username, password), headers=headers, data=json.dumps(payload))
        
#         if panel_response.status_code == 200:
#             panel_data = panel_response.json()
#             print(f"Data for panel {panel_id}:")
#             print(json.dumps(panel_data, indent=2))
#         else:
#             print(f"Failed to retrieve data for panel {panel_id}: {panel_response.status_code} - {panel_response.text}")
# else:
#     print(f"Failed to retrieve dashboard: {response.status_code} - {response.text}")
#-----------------------------------------------------------------------------------------

import requests
import json

# Grafana details
grafana_url = "https://op.cloudbuilders.io"
username = 'admin'
password = 'Imfine123$'
dashboard_uid = "opentelemetry-apm"
datasource_id = "dds0jxfdwvo5cb" 
query= "sum(duration_milliseconds_count{span_kind=\"SPAN_KIND_SERVER\", service_name=\"$app\", http_route=~\"$route\"}) by(service_name)"

# Specify the time range (example: last 24 hours)
from_time = "2023-08-23T12:32:36Z"  # Start date in ISO format
to_time = "2023-08-23T12:48:13Z"    # End date in ISO format

# API endpoint to get the dashboard
url = f"{grafana_url}/api/dashboards/uid/{dashboard_uid}"

# Make the request with basic authentication
response = requests.get(url, auth=(username, password))

# Check if the request was successful
if response.status_code == 200:
    dashboard_data = response.json()
    
    # Iterate over panels to retrieve data
    for panel in dashboard_data['dashboard']['panels']:
        panel_id = panel['id']
        
        # # Retrieve the data source ID or name associated with the panel
        # datasource_name = panel.get('datasource')
        
        # if not datasource_name:
        #     print(f"No data source found for panel {panel_id}. Skipping...")
        #     continue
        
        # # Get data source details (name or ID)
        # datasource_url = f"{grafana_url}/api/datasources/name/{datasource_name}"
        # datasource_response = requests.get(datasource_url, auth=(username, password))
        
        # if datasource_response.status_code != 200:
        #     print(f"Failed to retrieve data source: {datasource_response.status_code} - {datasource_response.text}")
        #     continue
        
        # datasource = datasource_response.json()
        # datasource_id = datasource['id']
        
        # URL to query the data for a specific panel
        panel_query_url = f"{grafana_url}/api/ds/query"
        
        # Payload for the data query
        payload = {
            # "queries": [
            #     {
            #         "panelId": panel_id,
            #         "datasourceId": datasource_id,  # Add the data source ID here
            #         "range": {
            #             "from": from_time,
            #             "to": to_time
            #         },
            #         "intervalMs": 60000,  # Interval in milliseconds (adjust if needed)
            #         "maxDataPoints": 500,  # Maximum number of data points to return
            #     }
            # ]
            "queries": [
                {
                    "refId": "A",  # Identifier for the query, can be anything
                    "datasourceId": datasource_id,  # Use the known data source ID
                    "intervalMs": 60000,  # Interval in milliseconds (adjust if needed)
                    "maxDataPoints": 500,  # Maximum number of data points to return
                    "panelId": panel_id,
                    "range": {
                        "from": from_time,
                        "to": to_time
                    },
                    "targets": [
                        {
                            "expr": query,  # Replace with a valid Prometheus query
                            "format": "time_series"
                        }
                    ],
                }
            ],
            "range": {
                "from": from_time,
                "to": to_time
            },
            "interval": "1m",
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Request data from the panel
        panel_response = requests.post(panel_query_url, auth=(username, password), headers=headers, data=json.dumps(payload))
        
        if panel_response.status_code == 200:
            panel_data = panel_response.json()
            print(f"Data for panel {panel_id}:")
            print(json.dumps(panel_data, indent=2))
        else:
            print(f"Failed to retrieve data for panel {panel_id}: {panel_response.status_code} - {panel_response.text}")
else:
    print(f"Failed to retrieve dashboard: {response.status_code} - {response.text}")

