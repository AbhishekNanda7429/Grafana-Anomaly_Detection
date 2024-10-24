#duration_milliseconds_sum
#-------------------

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
        self.df = pd.read_csv(self.file_path)
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

    def send_data_to_api(self):
        """
        Send data to the API in the same format as the Isolation Forest model.
        Each dictionary contains the timestamp, value, and an is_anomaly flag.
        """
        # Convert the entire dataset (including anomaly status) to a list of dictionaries
        all_data = []
        for index, row in self.df.iterrows():
            all_data.append({
                "timestamp": row['ds'].isoformat(),  # Ensure timestamp is in ISO format
                "value": row['y'],  # The actual value
                "is_anomaly": row["anomaly"]  # True if anomaly, False otherwise
            })

        # Send the full dataset to the Flask API
        response = requests.post(self.api_url, json={"data": all_data})

        # Check the response from the Flask API
        if response.status_code == 200:
            print(f"Successfully sent {len(self.df)} rows of data to the API.")
        else:
            print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")

    def print_data_summary(self):
        # Print out some of the data for debugging
        print(f"Total data sent: {len(self.df)}")
        print(self.df.head())
