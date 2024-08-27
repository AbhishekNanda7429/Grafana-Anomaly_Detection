import requests
import json

# Configuration
PROMETHEUS_ENDPOINT = 'http://3.82.60.81:9090/'

def fetch_metrics(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text

def prometheus_to_json(prometheus_data):
    # Convert Prometheus text format to JSON (basic example, you may need a more advanced parser)
    lines = prometheus_data.split('\n')
    metrics = {}
    for line in lines:
        if line and not line.startswith('#'):
            parts = line.split(' ', 1)
            if len(parts) == 2:
                metric_name = parts[0]
                value = parts[1]
                metrics[metric_name] = value
    return json.dumps(metrics, indent=4)

def save_to_file(json_data, filename):
    with open(filename, 'w') as file:
        file.write(json_data)

def main():
    prometheus_data = fetch_metrics(PROMETHEUS_ENDPOINT)
    json_data = prometheus_to_json(prometheus_data)
    save_to_file(json_data, 'metrics_data.json')
    print('Metrics successfully saved to metrics_data.json')

if __name__ == "__main__":
    main()
