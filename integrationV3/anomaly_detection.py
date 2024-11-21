# # anomaly_detection.py

# import os
# import pandas as pd
# import pickle
# import boto3
# from sklearn.ensemble import IsolationForest
# from botocore.exceptions import NoCredentialsError

# class AnomalyDetectionModel:
#     def __init__(self, threshold_multiplier, data):
#         self.threshold_multiplier = threshold_multiplier
#         self.data = data  # Accepting DataFrame directly
#         self.var = None  # Variable name will be determined from the first column after indexing
#         self.model = None

#     def load_data(self):
#         # Validate the dataset has a 'Time' column
#         if 'Time' not in self.data.columns:
#             raise ValueError("The dataset must have a 'Time' column.")
        
#         # Convert 'Time' to datetime and set as index
#         self.data['Time'] = pd.to_datetime(self.data['Time'])
#         self.data.set_index('Time', inplace=True)

#         # Drop rows with NaN values
#         self.data = self.data.dropna()

#         # Validate the dataset has at least one other column after 'Time'
#         if len(self.data.columns) < 1:
#             raise ValueError("The dataset must have at least one column besides 'Time'.")

#         # Set the target value column to the first column in the DataFrame after indexing
#         self.var = self.data.columns[0]
#         print(f"Target value column detected: {self.var}")

#     def calculate_rolling_statistics(self):
#         # Determine sampling interval and window size
#         self.data['Time_Diff'] = self.data.index.to_series().diff().dt.total_seconds()
#         average_interval = self.data['Time_Diff'].mean()
#         points_per_hour = int(3600 / average_interval)

#         # Calculate rolling mean and standard deviation
#         self.data['Rolling_Mean'] = self.data[self.var].rolling(window=points_per_hour).mean()
#         self.data['Rolling_Std'] = self.data[self.var].rolling(window=points_per_hour).std()

#         # Define upper and lower bounds
#         self.data['Upper_Bound'] = self.data['Rolling_Mean'] + (self.threshold_multiplier * self.data['Rolling_Std'])
#         self.data['Lower_Bound'] = self.data['Rolling_Mean'] - (self.threshold_multiplier * self.data['Rolling_Std'])

#         # Drop rows with NaN values after rolling calculations
#         self.data.dropna(inplace=True)

#     def calculate_residuals(self):
#         # Calculate residuals for anomaly detection
#         self.data['Residual'] = self.data[self.var] - self.data['Rolling_Mean']

#     def train_isolation_forest(self):
#         # Train Isolation Forest on residuals
#         self.model = IsolationForest(contamination=0.01, n_estimators=200, max_samples=0.8, random_state=42)
#         self.model.fit(self.data[['Residual']])
#         self.data['ML_Anomaly'] = self.model.predict(self.data[['Residual']])
#         self.data['ML_Anomaly'] = self.data['ML_Anomaly'].map({1: 0, -1: 1})

#     def detect_anomalies(self):
#         # Detect anomalies using threshold and ML methods
#         self.data['Threshold_Anomaly'] = (
#             (self.data[self.var] > self.data['Upper_Bound']) |
#             (self.data[self.var] < self.data['Lower_Bound'])
#         )
#         self.data['Hybrid_Anomaly'] = self.data['Threshold_Anomaly'] | self.data['ML_Anomaly'].astype(bool)

#     def save_model(self, model_filename):
#         # Save the model to the specified file
#         with open(model_filename, 'wb') as file:
#             pickle.dump(self.model, file)
#         print(f"Model temporarily saved to {model_filename}")
#         return model_filename

#     def upload_to_s3(self, model_filename, bucket_name, s3_folder_path):
#         """
#         Uploads a file to an S3 bucket in a specified folder path.

#         Parameters:
#         - model_filename (str): Local path to the file to upload
#         - bucket_name (str): Name of the target S3 bucket
#         - s3_folder_path (str): Folder path within the S3 bucket
#         """
#         s3_file_path = f"{s3_folder_path}/{model_filename.split('/')[-1]}"
        
#         # Initialize the S3 client
#         s3 = boto3.client('s3')
        
#         try:
#             s3.upload_file(model_filename, bucket_name, s3_file_path)
#             print(f"File {model_filename} uploaded to {bucket_name}/{s3_file_path}")
#         except FileNotFoundError:
#             print(f"The file {model_filename} was not found.")
#         except NoCredentialsError:
#             print("Credentials not available for AWS S3 access.")
#         except Exception as e:
#             print(f"An error occurred: {e}")

#     def run_pipeline(self, bucket_name, s3_folder_path):
#         # Load data and validate the target column
#         self.load_data()

#         # Ensure self.var is set and sanitize the variable name
#         if not self.var:
#             raise ValueError("Target variable name (self.var) is not set. Ensure the dataset has valid columns.")
#         safe_var_name = str(self.var).replace("/", "_").replace(" ", "_")
#         model_filename = f"{safe_var_name}_model.pkl"

#         # Perform calculations and anomaly detection
#         self.calculate_rolling_statistics()
#         self.calculate_residuals()
#         self.train_isolation_forest()
#         self.detect_anomalies()

#         # Save the model locally and upload to S3
#         self.save_model(model_filename)
#         self.upload_to_s3(model_filename, bucket_name, s3_folder_path)

#         # Remove temporary local file after upload
#         os.remove(model_filename)
#         print(f"Temporary file {model_filename} deleted after upload.")
#==================================================================

# import os
# import pandas as pd
# import pickle
# import boto3
# from sklearn.ensemble import IsolationForest
# from botocore.exceptions import NoCredentialsError

# class AnomalyDetectionModel:
#     def __init__(self, threshold_multiplier, data):
#         """
#         Initialize the AnomalyDetectionModel with a threshold multiplier and dataset.
#         """
#         self.threshold_multiplier = threshold_multiplier
#         self.data = data
#         self.var = None  # Variable name will be determined dynamically
#         self.model = None

#     def load_data(self):
#         """
#         Prepare the data by setting 'Time' as the index and ensuring it's clean.
#         """
#         if 'Time' not in self.data.columns:
#             raise ValueError("The dataset must have a 'Time' column.")

#         self.data['Time'] = pd.to_datetime(self.data['Time'])
#         self.data.set_index('Time', inplace=True)
#         self.data.dropna(inplace=True)

#         if len(self.data.columns) < 1:
#             raise ValueError("The dataset must have at least one column besides 'Time'.")

#         self.var = self.data.columns[0]
#         print(f"Target value column detected: {self.var}")

#     def calculate_rolling_statistics(self):
#         """
#         Calculate rolling mean and standard deviation for anomaly thresholds.
#         """
#         self.data['Time_Diff'] = self.data.index.to_series().diff().dt.total_seconds()
#         average_interval = self.data['Time_Diff'].mean()
#         points_per_hour = int(3600 / average_interval)

#         self.data['Rolling_Mean'] = self.data[self.var].rolling(window=points_per_hour).mean()
#         self.data['Rolling_Std'] = self.data[self.var].rolling(window=points_per_hour).std()
#         self.data['Upper_Bound'] = self.data['Rolling_Mean'] + (self.threshold_multiplier * self.data['Rolling_Std'])
#         self.data['Lower_Bound'] = self.data['Rolling_Mean'] - (self.threshold_multiplier * self.data['Rolling_Std'])
#         self.data.dropna(inplace=True)

#     def calculate_residuals(self):
#         """
#         Compute residuals for anomaly detection.
#         """
#         self.data['Residual'] = self.data[self.var] - self.data['Rolling_Mean']

#     def train_isolation_forest(self):
#         """
#         Train the Isolation Forest model for anomaly detection.
#         """
#         self.model = IsolationForest(contamination=0.01, n_estimators=200, max_samples=0.8, random_state=42)
#         self.model.fit(self.data[['Residual']])
#         self.data['ML_Anomaly'] = self.model.predict(self.data[['Residual']])
#         self.data['ML_Anomaly'] = self.data['ML_Anomaly'].map({1: 0, -1: 1})

#     def detect_anomalies(self):
#         """
#         Detect anomalies using a hybrid approach combining thresholds and ML results.
#         """
#         self.data['Threshold_Anomaly'] = (
#             (self.data[self.var] > self.data['Upper_Bound']) |
#             (self.data[self.var] < self.data['Lower_Bound'])
#         )
#         self.data['Hybrid_Anomaly'] = self.data['Threshold_Anomaly'] | self.data['ML_Anomaly'].astype(bool)

#     def save_model(self, model_filename):
#         """
#         Save the trained model to a local file.
#         """
#         with open(model_filename, 'wb') as file:
#             pickle.dump(self.model, file)
#         print(f"Model temporarily saved to {model_filename}")
#         return model_filename

#     def upload_to_s3(self, model_filename, bucket_name, s3_folder_path):
#         """
#         Upload the model file to an S3 bucket.
#         """
#         s3_file_path = f"{s3_folder_path}/{model_filename.split('/')[-1]}"
#         s3 = boto3.client('s3')

#         try:
#             s3.upload_file(model_filename, bucket_name, s3_file_path)
#             print(f"File {model_filename} uploaded to {bucket_name}/{s3_file_path}")
#         except FileNotFoundError:
#             raise FileNotFoundError(f"The file {model_filename} was not found.")
#         except NoCredentialsError:
#             raise NoCredentialsError("Credentials not available for AWS S3 access.")
#         except Exception as e:
#             raise Exception(f"An error occurred: {e}")

#     def run_pipeline(self, bucket_name, s3_folder_path):
#         """
#         Execute the full pipeline and save the trained model to S3.
#         """
#         self.load_data()
#         safe_var_name = str(self.var).replace("/", "_").replace(" ", "_")
#         model_filename = f"{safe_var_name}_model.pkl"

#         self.calculate_rolling_statistics()
#         self.calculate_residuals()
#         self.train_isolation_forest()
#         self.detect_anomalies()

#         self.save_model(model_filename)
#         self.upload_to_s3(model_filename, bucket_name, s3_folder_path)
#         os.remove(model_filename)
#         print(f"Temporary file {model_filename} deleted after upload.")
#========================================================

# # anomaly_detection.py

import os
import pandas as pd
import pickle
import boto3
from sklearn.ensemble import IsolationForest
from botocore.exceptions import NoCredentialsError


class AnomalyDetectionModel:
    def __init__(self, threshold_multiplier, data, csv_filename=None):
        """
        Initialize the AnomalyDetectionModel with a threshold multiplier, dataset, and optional input CSV filename.
        """
        self.threshold_multiplier = threshold_multiplier
        self.data = data
        self.var = None  # Target column will be set dynamically
        self.model = None
        self.csv_filename = csv_filename  # Original input CSV filename

    def load_data(self):
        """
        Prepare the data by setting 'Time' as the index and ensuring it's clean.
        """
        if 'Time' not in self.data.columns:
            raise ValueError("The dataset must have a 'Time' column.")

        self.data['Time'] = pd.to_datetime(self.data['Time'])
        self.data.set_index('Time', inplace=True)
        self.data.dropna(inplace=True)

        if len(self.data.columns) < 1:
            raise ValueError("The dataset must have at least one column besides 'Time'.")

        self.var = self.data.columns[0]  # Set the target column as the first column after 'Time'
        print(f"Target value column detected: {self.var}")

    def calculate_rolling_statistics(self):
        """
        Calculate rolling mean and standard deviation for anomaly thresholds.
        """
        print(f"Data shape before rolling stats: {self.data.shape}")
        
        self.data['Time_Diff'] = self.data.index.to_series().diff().dt.total_seconds()
        average_interval = self.data['Time_Diff'].mean()
        points_per_hour = int(3600 / average_interval)

        # Safeguard to ensure the rolling window size doesn't exceed available data points
        points_per_hour = max(1, min(points_per_hour, len(self.data)))

        self.data['Rolling_Mean'] = self.data[self.var].rolling(window=points_per_hour).mean()
        self.data['Rolling_Std'] = self.data[self.var].rolling(window=points_per_hour).std()
        self.data['Upper_Bound'] = self.data['Rolling_Mean'] + (self.threshold_multiplier * self.data['Rolling_Std'])
        self.data['Lower_Bound'] = self.data['Rolling_Mean'] - (self.threshold_multiplier * self.data['Rolling_Std'])
        self.data.dropna(inplace=True)

    def calculate_residuals(self):
        """
        Compute residuals for anomaly detection.
        """
        self.data['Residual'] = self.data[self.var] - self.data['Rolling_Mean']

    def train_isolation_forest(self):
        """
        Train the Isolation Forest model for anomaly detection.
        """
        print(f"Residuals data shape: {self.data[['Residual']].shape}")
        
        if self.data[['Residual']].empty:
            raise ValueError("No data available to train IsolationForest.")
        
        n_samples = len(self.data)
        
        # Dynamically set max_samples to ensure it is within valid range
        max_samples = min(0.8 * n_samples, n_samples)  # Use 80% of the data or total samples, whichever is smaller
        max_samples = max(1, int(max_samples))  # Ensure at least 1 sample is used
        
        print(f"Using max_samples={max_samples} for IsolationForest training.")
        
        self.model = IsolationForest(
            contamination=0.01,
            n_estimators=200,
            max_samples=max_samples,
            random_state=42
        )
        
        self.model.fit(self.data[['Residual']])
        self.data['ML_Anomaly'] = self.model.predict(self.data[['Residual']])
        self.data['ML_Anomaly'] = self.data['ML_Anomaly'].map({1: 0, -1: 1})

    def detect_anomalies(self):
        """
        Detect anomalies using a hybrid approach combining thresholds and ML results.
        """
        self.data['Threshold_Anomaly'] = (
            (self.data[self.var] > self.data['Upper_Bound']) |
            (self.data[self.var] < self.data['Lower_Bound'])
        )
        self.data['Hybrid_Anomaly'] = self.data['Threshold_Anomaly'] | self.data['ML_Anomaly'].astype(bool)

    def save_model(self, model_filename):
        """
        Save the trained model to a local file.
        """
        with open(model_filename, 'wb') as file:
            pickle.dump(self.model, file)
        print(f"Model temporarily saved to {model_filename}")
        return model_filename

    def upload_to_s3(self, model_filename, bucket_name, s3_folder_path):
        """
        Upload the model file to an S3 bucket.
        """
        s3_file_path = f"{s3_folder_path}/{model_filename.split('/')[-1]}"
        s3 = boto3.client('s3')

        try:
            s3.upload_file(model_filename, bucket_name, s3_file_path)
            print(f"File {model_filename} uploaded to {bucket_name}/{s3_file_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {model_filename} was not found.")
        except NoCredentialsError:
            raise NoCredentialsError("Credentials not available for AWS S3 access.")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

    def run_pipeline(self, bucket_name, s3_folder_path):
        """
        Execute the full pipeline and save the trained model to S3.
        """
        self.load_data()

        # Generate model filename based on input CSV filename
        if self.csv_filename:
            model_filename = self.csv_filename.replace("_result.csv", "_model.pkl")
        else:
            raise ValueError("CSV filename not provided for generating the model filename.")

        # Perform calculations and train the model
        self.calculate_rolling_statistics()
        self.calculate_residuals()
        self.train_isolation_forest()
        self.detect_anomalies()

        # Save the model and upload to S3
        self.save_model(model_filename)
        self.upload_to_s3(model_filename, bucket_name, s3_folder_path)

        # Clean up local model file
        os.remove(model_filename)
        print(f"Temporary file {model_filename} deleted after upload.")
