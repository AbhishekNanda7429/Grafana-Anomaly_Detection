import pandas as pd
import os

class DataCleaner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_and_clean_data(self):
        # Load the CSV file with low_memory set to False to avoid DtypeWarning
        self.df = pd.read_csv(self.file_path, low_memory=False)
        
        # Drop rows and columns with NaN values
        self.df.dropna(axis=0, how='any', inplace=True)  # Removes rows with NaN
        self.df.dropna(axis=1, how='any', inplace=True)  # Removes columns with NaN
        
        return self.df
    
    def save_cleaned_data(self, output_folder):
        # Ensure the output folder exists, create it if it doesn't
        os.makedirs(output_folder, exist_ok=True)
        
        # Extract the original filename without extension
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        
        # Create the new filename with '_cleaned' suffix
        cleaned_filename = f"{base_name}_cleaned.csv"
        
        # Define the path to save the cleaned DataFrame
        output_path = os.path.join(output_folder, cleaned_filename)
        
        # Save the DataFrame to the specified path
        self.df.to_csv(output_path, index=False)
        print(f"Cleaned data saved to: {output_path}")
