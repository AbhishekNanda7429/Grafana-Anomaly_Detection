# test_predict.py

import requests

# Define the API endpoint URL for prediction
url = "http://127.0.0.1:8000/predict/"

# Define the path to the CSV file you want to use for predictions
file_path = "C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET random_status3.csv"  # Replace with the path to your input CSV file

# Define the data payload with model parameters
data = {
    "var": "random_status",        # Replace with the correct variable name used during training
    "model_folder": "models"    # Folder where the trained model is saved
}

# Open the file in binary mode for uploading
with open(file_path, 'rb') as file:
    # Send a POST request with file and payload
    files = {'file': (file_path, file, 'text/csv')}
    response = requests.post(url, files=files, data=data)

# Print the response
if response.status_code == 200:
    print("Prediction successful:")
    print(response.json())
else:
    print("Prediction failed:")
    print(response.status_code, response.text)


#------------------------------------------------

# test_train_model.py

# import requests

# # Define the API endpoint URL for training
# url = "http://127.0.0.1:8000/train_model/"

# # Define the payload with model parameters for training
# payload = {
#     "threshold_multiplier": 3.5,
#     "filepath": "C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET error_test3.csv",  # Replace with the path to your dataset file
#     "var": "error_test",  # Replace with the correct variable name in your dataset
#     #"model_folder": "models"  # Optional, the folder to save the trained model
# }

# # Send a POST request to the API for training
# response = requests.post(url, json=payload)

# # Print the response
# if response.status_code == 200:
#     print("Model training successful:")
#     print(response.json())
# else:
#     print("Model training failed:")
#     print(response.status_code, response.text)
