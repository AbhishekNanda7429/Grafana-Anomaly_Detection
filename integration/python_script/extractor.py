import os
import datetime
from datetime import datetime
# from GrafanaPrometheusDataFetcher import GrafanaPrometheusDataFetcher
from python_script.GrafanaPrometheusDataFetcher import GrafanaPrometheusDataFetcher
# from GrafanaDashboardProcessor import GrafanaDashboardProcessor
from python_script.GrafanaDashboardProcessor import GrafanaDashboardProcessor

class GrafanaDataExtractor:
    def __init__(self, grafana_url, api_key, dashboard_uid, username, password, timeframes):
        self.grafana_url = grafana_url
        self.api_key = api_key
        self.dashboard_uid = dashboard_uid
        self.username = username
        self.password = password
        self.timeframes = timeframes
        
        # Initialize processor
        self.processor = GrafanaDashboardProcessor(
            grafana_url=self.grafana_url,
            api_key=self.api_key,
            dashboard_uid=self.dashboard_uid,
            username=self.username,
            password=self.password,
            start_time_str=self.timeframes[0],
            end_time_str=self.timeframes[1]
        )
    
    def extract_data(self):
        # Fetch and process the dashboard data
        dashboard_data = self.processor.fetch_dashboard()
        data = self.processor.process_panels(dashboard_data)
        print ("data",)
        
        # Example usage of GrafanaPrometheusDataFetcher for fetching Prometheus data
        for uid in data:
            type_name = data[uid]['uid_details']['type_name']
            query_url = f"{self.grafana_url}/api/ds/query?ds_type={type_name}&requestId=explore_x25"
            fetcher = GrafanaPrometheusDataFetcher(self.grafana_url, self.username, self.password, query_url)
            
            from_time = fetcher.convert_to_timestamp(self.timeframes[0])
            to_time = fetcher.convert_to_timestamp(self.timeframes[1])

            # Convert to Unix timestamps
            timestamps = [int(datetime.strptime(time, '%Y-%m-%d %H:%M:%S').timestamp()) for time in self.timeframes]
            
            # Path to get resource names
            path = f"/api/datasources/uid/{uid}/resources/api/v1/label/__name__/values?start={timestamps[0]}&end={timestamps[1]}"
            expr_list = fetcher.get_resources(path=path)
            
            print("Metric Names:", expr_list)
            
            # Initialize main_df as a dictionary to hold DataFrames for each expr
            main_df = {}
            output_dir = 'dataframes'
            
            # Ensure the output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Loop through each metric and process data
            for expr in expr_list:
                body = fetcher.build_query_body(expr, from_time, to_time, type_name, uid)
                json_data = fetcher.fetch_data(body)
                
                if json_data:
                    # Process the data into a DataFrame
                    df = fetcher.process_data(json_data)
                    
                    # Save the DataFrame to a CSV file
                    df.to_csv(f'{output_dir}/{expr}.csv', index=False)

                    # Initialize the key in main_df if it doesn't exist
                    if expr not in main_df:
                        main_df[expr] = []
                    
                    # Append the DataFrame to the list for that metric
                    main_df[expr].append(df)
                    
                    # Print the DataFrame (table format)
                    print(f"Data for {expr}:")
        
        return main_df

# #Instantiate and call the extraction
# if __name__ == "__main__":
#     extractor = GrafanaDataExtractor(
#         grafana_url="https://op.cloudbuilders.io",
#         api_key="glsa_Y8WYTAWLM3BoHHDGYSUb86e59kbGkBIw_523e9ead",
#         dashboard_uid="opentelemetry-apm",
#         username='admin',
#         password='Imfine123$',
#         timeframes=['2024-10-15 13:06:55', '2024-10-25 14:06:55']
#     )
    
#     # data = extractor.extract_data()
