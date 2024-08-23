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
import requests
import json
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

GRAFANA_URL = "https://op.cloudbuilders.io"
username = 'admin'
password = 'Imfine123$'

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

def get_panel_data(panel, datasource, time_range):
    # This function will need to be adapted based on your specific data source
    # This example assumes a Prometheus-like query structure
    query = panel.get('targets', [{}])[0].get('expr', '')
    if not query:
        return None

    params = {
        'query': query,
        'start': time_range['from'],
        'end': time_range['to'],
        'step': '60s'  # adjust as needed
    }

    response = requests.get(f"{GRAFANA_URL}/api/datasources/proxy/{datasource['id']}/api/v1/query_range", 
                            auth=HTTPBasicAuth(username, password), params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for panel {panel['title']}: {response.status_code}")
        return None

# Get all dashboards
response = requests.get(f"{GRAFANA_URL}/api/search", auth=HTTPBasicAuth(username, password))
dashboards = response.json()

# Set time range for data queries (last 24 hours)
now = datetime.now()
time_range = {
    'from': (now - timedelta(hours=24)).isoformat(),
    'to': now.isoformat()
}

# Fetch details for each dashboard
# for dashboard in dashboards:
#     uid = dashboard['uid']
#     response = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", auth=HTTPBasicAuth(username, password))
#     dashboard_data = response.json()
    
#     print(f"\nDashboard: {dashboard['title']}")
    
#     # Get datasource info
#     datasource_response = requests.get(f"{GRAFANA_URL}/api/datasources", auth=HTTPBasicAuth(username, password))
#     datasources = {ds['name']: ds for ds in datasource_response.json()}
    
#     # Process each panel in the dashboard
#     for panel in dashboard_data['dashboard']['panels']:
#         print(f"\n  Panel: {panel['title']}")
        
#         # Get datasource for this panel
#         datasource_name = panel.get('datasource', {}).get('type', 'default')
#         datasource = datasources.get(datasource_name)
        
#         if not datasource:
#             print(f"    Error: Datasource {datasource_name} not found")
#             continue
        
#         # Fetch data for the panel
#         panel_data = get_panel_data(panel, datasource, time_range)
        
#         if panel_data:
#             # Process and print data (customize based on your needs)
#             results = panel_data.get('data', {}).get('result', [])
#             for result in results:
#                 metric = result.get('metric', {})
#                 values = result.get('values', [])
#                 print(f"    Metric: {metric}")
#                 print(f"    Data points: {len(values)}")
#                 if values:
#                     print(f"    Latest value: {values[-1]}")
#         else:
#             print("    No data available for this panel")
# Fetch details for each dashboard
for dashboard in dashboards:
    uid = dashboard['uid']
    response = requests.get(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", auth=HTTPBasicAuth(username, password))
    dashboard_data = response.json()
    
    print(f"\nDashboard: {dashboard['title']}")
    
    # Check if 'dashboard' key exists
    if 'dashboard' not in dashboard_data:
        print(f"  Error: 'dashboard' key not found in the response for {dashboard['title']}")
        print(f"  Response keys: {list(dashboard_data.keys())}")
        continue
    
    # Get the actual dashboard content
    dashboard_content = dashboard_data['dashboard']
    
    # Check if 'panels' key exists
    if 'panels' not in dashboard_content:
        print(f"  Note: 'panels' key not found in dashboard {dashboard['title']}")
        print(f"  Dashboard keys: {list(dashboard_content.keys())}")
        
        # Check if the dashboard uses rows
        if 'rows' in dashboard_content:
            print("  This dashboard uses rows. Processing row panels...")
            panels = [panel for row in dashboard_content['rows'] for panel in row.get('panels', [])]
        else:
            print("  Unable to find panels or rows in this dashboard.")
            continue
    else:
        panels = dashboard_content['panels']
    
    # Get datasource info
    datasource_response = requests.get(f"{GRAFANA_URL}/api/datasources", auth=HTTPBasicAuth(username, password))
    datasources = {ds['name']: ds for ds in datasource_response.json()}
    
    # Process each panel
    for panel in panels:
        print(f"\n  Panel: {panel['title']}")
        
        # ... (rest of the code remains the same)