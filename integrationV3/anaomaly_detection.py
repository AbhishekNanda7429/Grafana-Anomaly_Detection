# anomaly_detection_model.py

import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import pickle

class AnomalyDetectionModel:
    def __init__(self, threshold_multiplier, filepath, var):
        self.threshold_multiplier = threshold_multiplier
        self.filepath = filepath
        self.var = var
        self.model = None
        self.data = None

    def load_data(self):
        # Load dataset and preprocess
        self.data = pd.read_csv(self.filepath)
        self.data['Time'] = pd.to_datetime(self.data['Time'])
        self.data.set_index('Time', inplace=True)
        self.data = self.data.dropna()

    def calculate_rolling_statistics(self):
        # Determine sampling interval and window size
        self.data['Time_Diff'] = self.data.index.to_series().diff().dt.total_seconds()
        average_interval = self.data['Time_Diff'].mean()
        points_per_hour = int(3600 / average_interval)

        # Calculate rolling mean and std deviation
        self.data['Rolling_Mean'] = self.data[f'GET /{self.var}'].rolling(window=points_per_hour).mean()
        self.data['Rolling_Std'] = self.data[f'GET /{self.var}'].rolling(window=points_per_hour).std()

        # Define upper and lower bounds
        self.data['Upper_Bound'] = self.data['Rolling_Mean'] + (self.threshold_multiplier * self.data['Rolling_Std'])
        self.data['Lower_Bound'] = self.data['Rolling_Mean'] - (self.threshold_multiplier * self.data['Rolling_Std'])
        self.data.dropna(inplace=True)  # Drop NaNs after rolling calculations

    def calculate_residuals(self):
        # Calculate residuals for anomaly detection
        self.data['Residual'] = self.data[f'GET /{self.var}'] - self.data['Rolling_Mean']

    def train_isolation_forest(self):
        # Train Isolation Forest on residuals
        self.model = IsolationForest(contamination=0.01, n_estimators=200, max_samples=0.8, random_state=42)
        self.model.fit(self.data[['Residual']])
        self.data['ML_Anomaly'] = self.model.predict(self.data[['Residual']])
        self.data['ML_Anomaly'] = self.data['ML_Anomaly'].map({1: 0, -1: 1})

    def detect_anomalies(self):
        # Detect anomalies using threshold and ML methods
        self.data['Threshold_Anomaly'] = (
            (self.data[f'GET /{self.var}'] > self.data['Upper_Bound']) |
            (self.data[f'GET /{self.var}'] < self.data['Lower_Bound'])
        )
        self.data['Hybrid_Anomaly'] = self.data['Threshold_Anomaly'] | self.data['ML_Anomaly'].astype(bool)

    def save_model(self, model_folder="models"):
        # Save the model to the specified folder
        os.makedirs(model_folder, exist_ok=True)
        model_filename = os.path.join(model_folder, f"{self.var}_model.pkl")
        with open(model_filename, 'wb') as file:
            pickle.dump(self.model, file)
        print(f"Model saved to {model_filename}")

    # def plot_results(self):
    #     # Plotting results with anomalies highlighted
    #     plt.figure(figsize=(15, 6))
    #     plt.plot(self.data.index, self.data[f'GET /{self.var}'], label=f'GET /{self.var}')
    #     plt.plot(self.data.index, self.data['Upper_Bound'], color='green', linestyle='--', label='Upper Bound')
    #     plt.plot(self.data.index, self.data['Lower_Bound'], color='red', linestyle='--', label='Lower Bound')
    #     plt.scatter(self.data[self.data['Hybrid_Anomaly'] == 1].index,
    #                 self.data[self.data['Hybrid_Anomaly'] == 1][f'GET /{self.var}'],
    #                 color='purple', label='Hybrid Anomaly', marker='x')
    #     plt.xlabel('Time')
    #     plt.ylabel(f'GET /{self.var} Value')
    #     plt.title(f'Hybrid Anomaly Detection in GET /{self.var} Over Time')
    #     plt.legend()
    #     plt.show()

    def run_pipeline(self, model_folder="models"):
        self.load_data()
        self.calculate_rolling_statistics()
        self.calculate_residuals()
        self.train_isolation_forest()
        self.detect_anomalies()
        self.save_model(model_folder)
        # self.plot_results()
