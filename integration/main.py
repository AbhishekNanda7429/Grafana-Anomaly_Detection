from models.isolation_forest import IsolationForestModel
from models.prophet_model import ProphetModel

# Example usage for two datasets
if __name__ == "__main__":
    # Dataset 1 calls_total
    file_path_1 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\calls_total_df.csv'  
    api_url_1 = 'http://localhost:5000/calls-total'  # Your Flask API endpoint
    
    anomaly_detector_1 = IsolationForestModel(file_path_1, api_url_1)
    anomaly_detector_1.load_and_preprocess_data()
    anomaly_detector_1.detect_anomalies()
    anomaly_detector_1.send_data_to_api()
    anomaly_detector_1.print_data_summary()

    # Dataset 2 scrape_duration_seconds
    file_path_2 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\scrape_duration_seconds_df.csv'  
    api_url_2 = 'http://localhost:5000/scrape-duration-seconds'  # Another Flask API endpoint
    
    anomaly_detector_2 = IsolationForestModel(file_path_2, api_url_2)
    anomaly_detector_2.load_and_preprocess_data()
    anomaly_detector_2.detect_anomalies()
    anomaly_detector_2.send_data_to_api()
    anomaly_detector_2.print_data_summary()

    #Dataset 3 duration_milliseconds_sum
    file_path_3 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\duration_ms_sum_df.csv'  
    api_url_3 = 'http://localhost:5000/duration-milliseconds-sum'  # Another Flask API endpoint
    
    anomaly_detector_3 = ProphetModel(file_path_3, api_url_3)
    anomaly_detector_3.load_data()
    anomaly_detector_3.fit_model()
    anomaly_detector_3.make_predictions()
    anomaly_detector_3.detect_anomalies()
    anomaly_detector_3.send_data_to_api()
    anomaly_detector_3.print_data_summary()

    #Dataset 4 duration_millisecond_bucket
    file_path_4 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\Anomaly_grafana\\dataframes\\duration_ms_bucket_df.csv'  
    api_url_4 = 'http://localhost:5000/duration-milliseconds-bucket'  # Another Flask API endpoint
    
    anomaly_detector_4 = IsolationForestModel(file_path_4, api_url_4)
    anomaly_detector_4.load_and_preprocess_data()
    anomaly_detector_4.detect_anomalies()
    anomaly_detector_4.send_data_to_api()
    anomaly_detector_4.print_data_summary()
