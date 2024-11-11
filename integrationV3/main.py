from anaomaly_detection import AnomalyDetectionModel


filepath1= 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET error_test3.csv'
filepath2= 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET chain3.csv'
filepath3= 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET cpu_task3.csv'
filepath4= 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET io_task3.csv'
filepath5= 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET random_sleep3.csv'
filepath6= 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET random_status3.csv'
# filepath7= 'C:\\Users\\abhis\\Desktop\\CloudBuilders\\Grafana-Anomaly\\Grafana-Anomaly_Detection\\newData\\GET error_test3.csv'

# Define the configurations for each dataset
datasets = [
    {"file_path": filepath1, "threshold_multiplier": 3.5, "model_name": "model_dataset1.pkl", "var": "error_test"},
    {"file_path": filepath2, "threshold_multiplier": 3.5, "model_name": "model_dataset2.pkl", "var": "chain"},
    {"file_path": filepath3, "threshold_multiplier": 3.5, "model_name": "model_dataset3.pkl", "var": "cpu_task"},
    {"file_path": filepath4, "threshold_multiplier": 2.5, "model_name": "model_dataset4.pkl", "var": "io_task"},
    {"file_path": filepath5, "threshold_multiplier": 3.5, "model_name": "model_dataset5.pkl", "var": "random_sleep"},
    {"file_path": filepath6, "threshold_multiplier": 3.5, "model_name": "model_dataset6.pkl", "var": "random_status"},
    # Add more configurations as needed
]

# Run the anomaly detection pipeline for each dataset
for dataset in datasets:
    model = AnomalyDetectionModel(
        threshold_multiplier=dataset['threshold_multiplier'],
        filepath=dataset['file_path'],
        var=dataset['var']
    )
    model.run_pipeline(model_folder="models")
