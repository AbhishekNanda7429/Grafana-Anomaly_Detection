from models.isolation_forest import IsolationForestModel
from models.prophet_model import ProphetModel
from models.adtk_model import ADTKAnomalyDetector
from python_script.extractor import GrafanaDataExtractor

# Example usage for two datasets
if __name__ == "__main__":

    #extract data from grafana and store as csv df
    extractor = GrafanaDataExtractor(
        grafana_url="https://op.cloudbuilders.io",
        api_key="glsa_Y8WYTAWLM3BoHHDGYSUb86e59kbGkBIw_523e9ead",
        dashboard_uid="opentelemetry-apm",
        username='admin',
        password='Imfine123$',
        timeframes=['2024-10-15 13:06:55', '2024-10-25 14:06:55']
    )
    data = extractor.extract_data()

    #Dataset 1 calls_total 
    file_path_1 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\integration\\dataframes\\calls_total.csv'  
    api_url_1 = 'http://localhost:5000/calls-total'  
    
    anomaly_detector_1 = IsolationForestModel(file_path_1, api_url_1)
    anomaly_detector_1.load_and_preprocess_data()
    anomaly_detector_1.detect_anomalies()
    anomaly_detector_1.send_anomalies_to_api()
    anomaly_detector_1.print_data_summary()

    # Dataset 2 scrape_duration_seconds
    file_path_2 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\integration\\dataframes\\scrape_duration_seconds.csv'  
    api_url_2 = 'http://localhost:5000/scrape-duration-seconds'  
    
    anomaly_detector_2 = IsolationForestModel(file_path_2, api_url_2)
    anomaly_detector_2.load_and_preprocess_data()
    anomaly_detector_2.detect_anomalies()
    anomaly_detector_2.send_anomalies_to_api()
    anomaly_detector_2.print_data_summary()

    #Dataset 3 duration_milliseconds_sum
    file_path_3 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\integration\\dataframes\\duration_milliseconds_sum.csv'  
    api_url_3 = 'http://localhost:5000/duration-milliseconds-sum'  
    
    anomaly_detector_3 = ProphetModel(file_path_3, api_url_3)
    anomaly_detector_3.load_data()
    anomaly_detector_3.fit_model()
    anomaly_detector_3.make_predictions()
    anomaly_detector_3.detect_anomalies()
    anomaly_detector_3.send_anomalies_to_api()
    anomaly_detector_3.print_data_summary()

    # #Dataset 4 duration_millisecond_bucket
    # file_path_4 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\integration\\dataframes\\duration_millisecond_bucket.csv'  
    # api_url_4 = 'http://localhost:5000/duration-milliseconds-bucket'  
    
    # anomaly_detector_4 = IsolationForestModel(file_path_4, api_url_4)
    # anomaly_detector_4.load_and_preprocess_data()
    # anomaly_detector_4.detect_anomalies()
    # anomaly_detector_4.send_data_to_api()
    # anomaly_detector_4.print_data_summary()

    #Dataset 5 duration_milliseconds_sum
    file_path_5 = 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\integration\\dataframes\\duration_milliseconds_count.csv'  
    api_url_5 = 'http://localhost:5000/duration-milliseconds-count'  
    
    anomaly_detector_5 = ADTKAnomalyDetector(file_path_5, api_url_5)
    anomaly_detector_5.train()
    anomaly_detector_5.predict_anomalies()
    anomaly_detector_5.send_anomalies_to_api()
