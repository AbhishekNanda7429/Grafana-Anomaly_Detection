#!/bin/bash
 
# Stop and remove the existing Docker container, if running
docker stop anomaly-detection-container || true
docker rm anomaly-detection-container || true
 
# Remove the existing Docker image
docker rmi anomaly-detection-image || true

#Remove the existing git folder
# rm -rf Grafana-Anomaly_Detection || true

#clone the github repo using git clone command
# git clone https://github.com/AbhishekNanda7429/Grafana-Anomaly_Detection.git
 
#go into that folder
# cd .\Grafana-Anomaly_Detection\integrationV3\

#Checkout to the dev branch
# git checkout feature/dev
 
# Pull the latest changes from the repo
# git pull
 
# Build the new Docker image
docker build -t anomaly-detection-image .
 
# Run the new Docker container
docker run --env-file .env -p 8000:8000 --name anomaly-detection-container anomaly-detection-image
 
# docker logs -f flask-container
