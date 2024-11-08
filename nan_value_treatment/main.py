from Nan_value_treatment import DataCleaner

# Example usage for two datasets
if __name__ == "__main__":


    file_path = "C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\segregated_data\\PR95 Latency-data-2024-11-07 17_18_56.csv"
    output_folder ="cleaned_df"
    cleaner = DataCleaner(file_path)
    cleaned_df = cleaner.load_and_clean_data()
    # Save the cleaned DataFrame to the specified folder
    cleaner.save_cleaned_data(output_folder)
    # cleaned_df.head()