# #calls_total & scrape_duration_seconds

# import requests
# import json
# from sklearn.ensemble import IsolationForest
# from sklearn.preprocessing import StandardScaler
# import pandas as pd

# # Load the CSV file into a pandas DataFrame
# file_path = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\calls_total_df.csv'  
# df_calls_total = pd.read_csv(file_path, low_memory=False)

# # Convert data types to best possible types
# df_converted = df_calls_total.convert_dtypes()

# # Select only numeric columns for interpolation
# numeric_cols = df_converted.select_dtypes(include=['number']).columns

# # Convert mixed-type columns to numeric, coercing errors to NaN
# for col in numeric_cols:
#     df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')

# # Convert IntegerArray columns to float64
# for col in numeric_cols:
#     if isinstance(df_converted[col].dtype, pd.Int64Dtype):
#         df_converted[col] = df_converted[col].astype('float64')

# # Convert FloatingArray columns to float64
# for col in numeric_cols:
#     if isinstance(df_converted[col].dtype, pd.Float64Dtype):
#         df_converted[col] = df_converted[col].astype('float64')

# # Perform interpolation on numeric columns only
# df_converted[numeric_cols] = df_converted[numeric_cols].interpolate()

# # Backward Fill to fill any remaining NaN values
# df_bfill = df_converted.bfill()

# # Forward Fill to handle any remaining NaN values
# df_ffill = df_bfill.ffill()

# # Creating the final DataFrame
# final_df = df_ffill

# # Convert 'Time' column to datetime and set as index
# final_df['Time'] = pd.to_datetime(final_df['Time'])
# final_df.set_index('Time', inplace=True)

# # Select all relevant numeric metric columns for anomaly detection
# metrics_columns = ['Value']  # Add other metric columns as needed
# metrics_data = final_df[metrics_columns]

# # Standardize the data
# scaler = StandardScaler()
# metrics_scaled = scaler.fit_transform(metrics_data)

# # Initialize the Isolation Forest model
# iso_forest = IsolationForest(n_estimators=100, contamination=0.001, random_state=42)

# # Fit the model and predict anomalies (-1 means anomaly, 1 means normal)
# final_df['anomaly'] = iso_forest.fit_predict(metrics_scaled)

# # Convert the entire dataset (including anomaly status) to a list of dictionaries
# all_data = []
# for index, row in final_df.iterrows():
#     all_data.append({
#         "timestamp": index.isoformat(),
#         "value": row["Value"],
#         "is_anomaly": row["anomaly"] == -1  # True if anomaly, False otherwise
#     })

# # Send the full dataset to the Flask API
# url = 'http://localhost:5000/calls-total'  # Update this URL to match your Flask API URL
# response = requests.post(url, json={"data": all_data})

# # Check the response from the Flask API
# if response.status_code == 200:
#     print(f"Successfully sent {len(final_df)} rows of data to the API.")
# else:
#     print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")

# # Print out some of the data for debugging
# print(f"Total data sent: {len(final_df)}")
# print(final_df.head())
#------------------------------------------------------
import requests
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd

class AnomalyDetection:
    def __init__(self, file_path, api_url, metrics_columns=None):
        self.file_path = file_path
        self.api_url = api_url
        self.df = None
        self.metrics_columns = ['Value']
        #metrics_columns if metrics_columns else ['Value']
        
    def load_and_preprocess_data(self):
        # Load the CSV file into a pandas DataFrame
        self.df = pd.read_csv(self.file_path, low_memory=False)

        # Convert data types to best possible types
        df_converted = self.df.convert_dtypes()

        # Select only numeric columns for interpolation
        numeric_cols = df_converted.select_dtypes(include=['number']).columns

        # Convert mixed-type columns to numeric, coercing errors to NaN
        for col in numeric_cols:
            df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')

        # Convert IntegerArray columns to float64
        for col in numeric_cols:
            if isinstance(df_converted[col].dtype, pd.Int64Dtype):
                df_converted[col] = df_converted[col].astype('float64')

        # Convert FloatingArray columns to float64
        for col in numeric_cols:
            if isinstance(df_converted[col].dtype, pd.Float64Dtype):
                df_converted[col] = df_converted[col].astype('float64')

        # Perform interpolation on numeric columns only
        df_converted[numeric_cols] = df_converted[numeric_cols].interpolate()

        # Backward Fill to fill any remaining NaN values
        df_bfill = df_converted.bfill()

        # Forward Fill to handle any remaining NaN values
        df_ffill = df_bfill.ffill()

        # Creating the final DataFrame
        self.df = df_ffill

        # Convert 'Time' column to datetime and set as index
        self.df['Time'] = pd.to_datetime(self.df['Time'])
        self.df.set_index('Time', inplace=True)

    def detect_anomalies(self):
        # Select relevant numeric metric columns for anomaly detection
        metrics_data = self.df[self.metrics_columns]

        # Standardize the data
        scaler = StandardScaler()
        metrics_scaled = scaler.fit_transform(metrics_data)

        # Initialize the Isolation Forest model
        iso_forest = IsolationForest(n_estimators=100, contamination=0.001, random_state=42)

        # Fit the model and predict anomalies (-1 means anomaly, 1 means normal)
        self.df['anomaly'] = iso_forest.fit_predict(metrics_scaled)

    def send_data_to_api(self):
        # Convert the entire dataset (including anomaly status) to a list of dictionaries
        all_data = []
        for index, row in self.df.iterrows():
            all_data.append({
                "timestamp": index.isoformat(),
                "value": row['Value'],  # Assuming the first metric column
                "is_anomaly": row["anomaly"] == -1  # True if anomaly, False otherwise
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
