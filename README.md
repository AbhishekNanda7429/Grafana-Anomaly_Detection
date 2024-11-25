# Grafana-Anomaly_Detection

uvicorn app:app --reload
 # Build the new Docker image
docker build -t anomaly-detection-image .
 
# Run the new Docker container
docker run --env-file .env -p 8000:8000 --name anomaly-detection-container anomaly-detection-image
has context menu