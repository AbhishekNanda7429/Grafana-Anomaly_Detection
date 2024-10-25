import os
import datetime
from datetime import datetime
from GrafanaPrometheusDataFetcher import GrafanaPrometheusDataFetcher
from GrafanaDashboardProcessor import GrafanaDashboardProcessor

def main():
    # Define necessary parameters
    GRAFANA_URL = "https://op.cloudbuilders.io"
    API_KEY = "glsa_Y8WYTAWLM3BoHHDGYSUb86e59kbGkBIw_523e9ead"
    DASHBOARD_UID = "opentelemetry-apm"
    
    username = 'admin'
    password = 'Imfine123$'
    timeframes = ['2024-10-15 13:06:55', '2024-10-25 14:06:55']
    
    # Create an instance of the processor
    processor = GrafanaDashboardProcessor(
        grafana_url=GRAFANA_URL,
        api_key=API_KEY,
        dashboard_uid=DASHBOARD_UID,
        username=username,
        password=password,
        start_time_str=timeframes[0],
        end_time_str=timeframes[1]
    )
    
    # Fetch and process the dashboard data
    dashboard_data = processor.fetch_dashboard()
    data = processor.process_panels(dashboard_data)
    
    # Example usage of GrafanaPrometheusDataFetcher for fetching Prometheus data
    for uid in data:
        type_name = data[uid]['uid_details']['type_name']
        query_url = f"{GRAFANA_URL}/api/ds/query?ds_type={type_name}&requestId=explore_x25"
        fetcher = GrafanaPrometheusDataFetcher(GRAFANA_URL, username, password, query_url)
        
        from_time = fetcher.convert_to_timestamp(timeframes[0])
        to_time = fetcher.convert_to_timestamp(timeframes[1])

        # Convert to Unix timestamps
        timestamps = [int(datetime.strptime(time, '%Y-%m-%d %H:%M:%S').timestamp()) for time in timeframes]
 
       
        # Path to get resource names (e.g., Prometheus metric names)
        path = f"/api/datasources/uid/{uid}/resources/api/v1/label/__name__/values?start={timestamps[0]}&end={timestamps[1]}"
        
        # Path to get resource names (e.g., Prometheus metric names)
        path = f"/api/datasources/uid/{uid}/resources/api/v1/label/__name__/values?start=1729834381&end=1729835281"
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
                # Save the data to a file
                # processor.save_to_file(f'{output_dir}/{expr}.json',json_data)
                
                
                # Process the data into a DataFrame
                df = fetcher.process_data(json_data)
                
                
                # Save the DataFrame to a CSV file
                df.to_csv(f'{output_dir}/{expr}.csv', index=False)

                # Plot the data
                # fetcher.plot_data(df, expr)
                
                # Initialize the key in main_df if it doesn't exist
                if expr not in main_df:
                    main_df[expr] = []
                
                # Append the DataFrame to the list for that metric
                main_df[expr].append(df)
                
                # Print the DataFrame (table format)
                print(f"Data for {expr}:")
                # print(df.to_string())  # This prints the entire DataFrame as a table
        
        # Print the final main_df dictionary
        # print(main_df)
        # test=main_df['calls_total']
        # print(test)
        
main()
