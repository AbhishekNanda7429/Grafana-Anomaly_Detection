# from sklearn.ensemble import IsolationForest
# from sklearn.preprocessing import StandardScaler
# import pickle
# import pandas as pd

# # Load the CSV file into a pandas DataFrame
# file_path = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\calls_total_df.csv'  
# df_calls_total = pd.read_csv(file_path, low_memory=False)

# # Display the first few rows to verify the data is loaded correctly
# # df_calls_total.head()

# # Display the number of NaN values in each column
# # print("NaN values in each column before treatment:")
# # print(df_calls_total.isna().sum())

# # Convert data types to best possible types
# df_converted = df_calls_total.convert_dtypes()

# # Select only numeric columns for interpolation
# numeric_cols = df_converted.select_dtypes(include=['number']).columns

# # Convert mixed-type columns to numeric, coercing errors to NaN
# for col in numeric_cols:
#     df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')

# # Convert IntegerArray columns to float64
# # This ensures compatibility with the interpolate method
# for col in numeric_cols:
#     if isinstance(df_converted[col].dtype, pd.Int64Dtype): # Check for Int64Dtype instead of Float64Dtype
#         df_converted[col] = df_converted[col].astype('float64')

# # Convert FloatingArray columns to float64
# for col in numeric_cols:
#     if isinstance(df_converted[col].dtype, pd.Float64Dtype):
#         df_converted[col] = df_converted[col].astype('float64')

# # Perform interpolation on numeric columns only
# df_converted[numeric_cols] = df_converted[numeric_cols].interpolate()

# # Check for any remaining NaN values after interpolation
# # print("NaN values after interpolation:")
# # print(df_converted.isna().sum())

# # Backward Fill to fill any remaining NaN values
# df_bfill = df_converted.bfill()

# # Check for any remaining NaN values after backward fill
# # print("NaN values after backward fill:")
# # print(df_bfill.isna().sum())

# # Forward Fill to handle any remaining NaN values
# df_ffill = df_bfill.ffill()

# # Check for any remaining NaN values after forward fill
# # print("NaN values after forward fill:")
# # print(df_ffill.isna().sum())

# # Creating the final DataFrame
# final_df = df_ffill

# # Display the first few rows of the final DataFrame
# # final_df.head()
# #model with only numerical anomalies (isolation_forest)

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

# # with open('isolation_forest_model.pkl', 'wb') as model_file:
# #     pickle.dump((scaler, iso_forest), model_file)  # Save both the scaler and model

# # print("Isolation Forest model and scaler trained and saved.")


# # Visualize the anomalies for each metric
# # for column in metrics_columns:
# #     plt.figure(figsize=(15, 6))
# #     plt.plot(final_df.index, final_df[column], label=column, color='blue')
# #     plt.scatter(final_df.index[final_df['anomaly'] == -1], final_df[column][final_df['anomaly'] == -1],
# #                 color='red', label='Anomaly', marker='x')
# #     plt.title(f'calls_total Isolation_Forest(num)')
# #     plt.xlabel('Time')
# #     plt.ylabel(column)
# #     plt.legend()
# #     plt.show()

# # Print out the anomalies
# anomalies = final_df[final_df['anomaly'] == -1]
# print(f"Number of anomalies detected: {len(anomalies)}")
# print(anomalies.head())
#----------------------------------------------------------------------------

import requests
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import pandas as pd

# Load the CSV file into a pandas DataFrame
file_path = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\calls_total_df.csv'  
df_calls_total = pd.read_csv(file_path, low_memory=False)

# Convert data types to best possible types
df_converted = df_calls_total.convert_dtypes()

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
final_df = df_ffill

# Convert 'Time' column to datetime and set as index
final_df['Time'] = pd.to_datetime(final_df['Time'])
final_df.set_index('Time', inplace=True)

# Select all relevant numeric metric columns for anomaly detection
metrics_columns = ['Value']  # Add other metric columns as needed
metrics_data = final_df[metrics_columns]

# Standardize the data
scaler = StandardScaler()
metrics_scaled = scaler.fit_transform(metrics_data)

# Initialize the Isolation Forest model
iso_forest = IsolationForest(n_estimators=100, contamination=0.001, random_state=42)

# Fit the model and predict anomalies (-1 means anomaly, 1 means normal)
final_df['anomaly'] = iso_forest.fit_predict(metrics_scaled)

# Extract the anomalies
anomalies = final_df[final_df['anomaly'] == -1]

# Convert the anomalies to a list of dictionaries for easy API sending
anomaly_data = []
for index, row in anomalies.iterrows():
    anomaly_data.append({
        "timestamp": index.isoformat(),
        "value": row["Value"],
        "is_anomaly": True
    })

# Send the anomaly data to the Flask API
url = 'http://localhost:5000/send-anomalies'  # Update this URL to match your Flask API URL
response = requests.post(url, json={"anomalies": anomaly_data})

# Check the response from the Flask API
if response.status_code == 200:
    print(f"Successfully sent {len(anomalies)} anomalies to the API.")
else:
    print(f"Failed to send anomalies. Status code: {response.status_code}, Response: {response.text}")

# Print out the anomalies for debugging
print(f"Number of anomalies detected: {len(anomalies)}")
print(anomalies.head())
