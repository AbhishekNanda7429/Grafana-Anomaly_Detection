from models.isolation_forest import AnomalyDetection

# Example usage for two datasets
if __name__ == "__main__":
    # Dataset 1
    file_path_1 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\calls_total_df.csv'  # Path relative to your project structure
    api_url_1 = 'http://localhost:5000/calls-total'  # Your Flask API endpoint
    
    anomaly_detector_1 = AnomalyDetection(file_path_1, api_url_1)
    anomaly_detector_1.load_and_preprocess_data()
    anomaly_detector_1.detect_anomalies()
    anomaly_detector_1.send_data_to_api()
    anomaly_detector_1.print_data_summary()

    # Dataset 2 (example for a second dataset)
    file_path_2 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\scrape_duration_seconds_df.csv'  # Path relative to your project structure
    api_url_2 = 'http://localhost:5000/scrape-duration-seconds'  # Another Flask API endpoint
    
    anomaly_detector_2 = AnomalyDetection(file_path_2, api_url_2)
    anomaly_detector_2.load_and_preprocess_data()
    anomaly_detector_2.detect_anomalies()
    anomaly_detector_2.send_data_to_api()
    anomaly_detector_2.print_data_summary()
