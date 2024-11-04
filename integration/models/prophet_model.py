#duration_milliseconds_sum - no anomaly
#--------------------

import os
import pandas as pd
from prophet import Prophet
import requests  

class ProphetModel:
    def __init__(self, file_path, api_url):
        """
        Initialize the ProphetModel class.
        
        :param file_path: Path to the CSV file.
        :param api_url: The API endpoint to which results will be sent.
        """
        self.file_path = file_path
        self.api_url = api_url
        self.df = None
        self.model = None
        self.forecast = None
    
    def load_data(self):
        """
        Load and prepare the dataset for Prophet.
        """
        self.df = pd.read_csv(self.file_path, low_memory=False)
        self.df.rename(columns={'Time': 'ds', 'Value': 'y'}, inplace=True)
        self.df['ds'] = pd.to_datetime(self.df['ds'])
    
    def fit_model(self):
        """
        Initialize and fit the Prophet model.
        """
        self.model = Prophet()
        self.model.fit(self.df[['ds', 'y']])
    
    def make_predictions(self, periods=100, freq='15s'):
        """
        Make future predictions using the Prophet model.
        
        :param periods: Number of future periods to predict.
        :param freq: Frequency of the predictions.
        """
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        self.forecast = self.model.predict(future)
    
    def detect_anomalies(self):
        """
        Detect anomalies where actual values fall outside the prediction interval.
        """
        self.df['yhat'] = self.forecast['yhat'][:len(self.df)]
        self.df['yhat_upper'] = self.forecast['yhat_upper'][:len(self.df)]
        self.df['yhat_lower'] = self.forecast['yhat_lower'][:len(self.df)]

        # Anomalies are where actual values fall outside prediction intervals
        self.df['anomaly'] = (self.df['y'] > self.df['yhat_upper']) | (self.df['y'] < self.df['yhat_lower'])

    def send_anomalies_to_api(self):
        """
        Send only anomalies to the API in the same format as the Isolation Forest model.
        Each dictionary contains the timestamp, value, and an is_anomaly flag.
        """
        # Filter the DataFrame for anomalies only
        anomalies_df = self.df[self.df['anomaly'] == True]

        # Convert anomalies to a list of dictionaries
        anomaly_data = [
            {
                "timestamp": row['ds'].isoformat(),  # Ensure timestamp is in ISO format
                "value": row['y'],  # The actual value
                "is_anomaly": True
            }
            for _, row in anomalies_df.iterrows()
        ]

        # Send only the anomalies to the Flask API
        response = requests.post(self.api_url, json={"data": anomaly_data})

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
        anomalies_df.to_csv(output_file_path, index=False)
        print(f"Anomalies saved to {output_file_path}")

    def print_data_summary(self):
        # Print out some of the data for debugging
        print(f"Total data sent: {len(self.df)}")
        print(self.df.head())
