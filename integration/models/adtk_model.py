#duration_milliseconds_count
#--------------------------

import os
import requests
import pandas as pd
from adtk.data import validate_series
from adtk.detector import ThresholdAD

class ADTKAnomalyDetector:
    def __init__(self, file_path, api_url, api_key=None):
        """
        Initializes the anomaly detector with API and file configuration.
        
        :param api_url: URL of the API endpoint to send anomalies.
        :param file_path: Path of the input file for naming the output anomaly file.
        :param api_key: API key if needed for authorization.
        """
        self.api_url = api_url
        self.file_path = file_path
        self.api_key = api_key
        self.model = None  # Threshold-based anomaly detector will be initialized in train
        self.data = None  # Initialize self.data to ensure it exists

    def train(self):
        """
        Loads data from the file, sets up threshold-based anomaly detection model, and validates the data.
        """
        # Verify that file_path is a local file
        if not os.path.isfile(self.file_path):
            print(f"File not found: {self.file_path}. Please provide a valid local file path.")
            return

        try:
            # Load data and set up time series
            df = pd.read_csv(self.file_path, low_memory=False)
            df['Time'] = pd.to_datetime(df['Time'])  # Convert 'Time' column to datetime
            df.set_index('Time', inplace=True)       # Set 'Time' as the index
            
            # Validate series for anomaly detection
            self.data = validate_series(df['Value'])  # Assuming 'Value' is the data column for anomaly detection

            # Set up the threshold-based anomaly detector
            high_threshold = self.data.mean() + 2 * self.data.std()
            low_threshold = self.data.mean() - 2 * self.data.std()
            self.model = ThresholdAD(high=high_threshold, low=low_threshold)

            print("Model setup with threshold-based detection completed.")
        except Exception as e:
            print(f"Error loading or setting up the model: {e}")

    def predict_anomalies(self):
        """
        Detects anomalies using the threshold-based model and returns them.
        
        :return: DataFrame of detected anomalies.
        """
        if self.data is None or self.model is None:
            print("Data not loaded or model not initialized. Please run the train method first.")
            return pd.DataFrame()  # Return an empty DataFrame if data is not available

        # Detect anomalies
        anomalies = self.model.detect(self.data)
        anomalies = anomalies[anomalies == True]  # Filter only the anomalies
        return anomalies

    def send_anomalies_to_api(self):
        """
        Processes and sends detected anomalies to the specified API endpoint.
        Saves anomalies to a CSV file with the modified filename.
        """
        # Predict anomalies
        anomalies = self.predict_anomalies()
        
        # Check if there are anomalies to send
        if anomalies.empty:
            print("No anomalies detected to send.")
            return

        # Convert anomalies into a DataFrame and add an 'anomaly' column
        anomalies_df = anomalies.to_frame(name="Value")
        anomalies_df['anomaly'] = -1  # Mark anomalies for consistency
        
        # Convert anomalies to a list of dictionaries
        anomaly_data = [
            {
                "timestamp": index.isoformat(),
                "value": row['Value'],
                "is_anomaly": True
            }
            for index, row in anomalies_df.iterrows()
        ]

        # Send only the anomalies to the Flask API
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(self.api_url, json={"data": anomaly_data}, headers=headers)

        # Check the response from the Flask API
        if response.status_code == 200:
            print(f"Successfully sent {len(anomalies_df)} anomalies to the API.")
        else:
            print(f"Failed to send anomalies. Status code: {response.status_code}, Response: {response.text}")

        # Prepare the output folder and anomaly CSV file path
        output_folder = "anomalies"
        os.makedirs(output_folder, exist_ok=True)

        # Get the input file name without extension and add '_anomalies.csv' suffix
        input_filename = os.path.splitext(os.path.basename(self.file_path))[0]
        output_file_path = os.path.join(output_folder, f"{input_filename}_anomalies.csv")

        # Save anomalies to the specified CSV file
        anomalies_df.to_csv(output_file_path)
        print(f"Anomalies saved to {output_file_path}")

