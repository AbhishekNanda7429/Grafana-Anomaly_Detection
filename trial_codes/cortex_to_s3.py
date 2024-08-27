import requests
import json
import boto3
from datetime import datetime

# Configuration
# CORTEX_URL = 'https://your-cortex-instance/api/v1/query'
CORTEX_URL = 'http://35.174.213.241:9009'
S3_BUCKET_NAME = 'cortex'
S3_KEY_PREFIX = 'cortex-data/'

# Define your Cortex query
QUERY = 'mysql_locks_total{customer_id="DB_Customer_2", kind="immediate"}'

# Step 1: Query data from Cortex
def query_cortex(cortex_url, query):
    response = requests.get(cortex_url, params={'query': query})
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

# Step 2: Process data and convert to JSON
def process_data(cortex_data):
    # Extract relevant data and format it
    results = cortex_data.get('data', {}).get('result', [])
    json_data = json.dumps(results, indent=4)
    return json_data

# Step 3: Upload JSON data to S3
def upload_to_s3(json_data, s3_bucket, s3_key):
    s3_client = boto3.client('s3')
    
    s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=json_data, ContentType='application/json')

def main():
    # Query Cortex
    cortex_data = query_cortex(CORTEX_URL, QUERY)
    
    # Process the data into JSON
    json_data = process_data(cortex_data)
    
    # Generate S3 key with a timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    s3_key = f"{S3_KEY_PREFIX}cortex_data_{timestamp}.json"
    
    # Upload to S3
    upload_to_s3(json_data, S3_BUCKET_NAME, s3_key)
    
    print(f"Data successfully uploaded to s3://{S3_BUCKET_NAME}/{s3_key}")

if __name__ == "__main__":
    main()
