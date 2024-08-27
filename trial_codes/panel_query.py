
#------------------------------------------------------------------------------
import requests

# Grafana API details
GRAFANA_URL = "https://op.cloudbuilders.io"
API_KEY = "glsa_Y8WYTAWLM3BoHHDGYSUb86e59kbGkBIw_523e9ead"
DASHBOARD_UID = "opentelemetry-apm"
#PANEL_ID = "4"  # ID of the panel you want to extract data from

# Set up the headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Get the dashboard JSON configuration
dashboard_url = f"{GRAFANA_URL}/api/dashboards/uid/{DASHBOARD_UID}"
response = requests.get(dashboard_url, headers=headers)
dashboard_data = response.json()

# # Extract the panel data (assuming you're querying a specific panel)
# for panel in dashboard_data['dashboard']['panels']:
#     if panel['id'] == int(PANEL_ID):
#         panel_query = panel['targets']
#         print(panel_query)  # This will print the Prometheus query used by the panel

# Loop through all panels in the dashboard
for panel in dashboard_data['dashboard']['panels']:
    panel_id = panel['id']
    panel_title = panel.get('title', 'Unnamed Panel')
    
    print(f"\nPanel ID: {panel_id}")
    print(f"Panel Title: {panel_title}")
    
    # Each panel can have multiple queries (targets)
    for target in panel.get('targets', []):
        # Check for the data source and query
        datasource = target.get('datasource', 'Unknown datasource')
        prom_query = target.get('expr', 'No query found')  # 'expr' is used for Prometheus queries
        
        print(f"Data Source: {datasource}")
        print(f"Prometheus Query: {prom_query}")