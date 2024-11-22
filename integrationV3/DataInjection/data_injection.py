import boto3
import pandas as pd
import io
import os
import logging
from datetime import datetime
import concurrent.futures

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3DataInjector:
    def __init__(self, s3_bucket_name, athena_database, aws_access_key_id, aws_secret_access_key, partition_granularity="minute"):
        """
        Initialize the S3 injector and Athena database configuration.

        Args:
            s3_bucket_name (str): S3 bucket name.
            athena_database (str): Athena database name.
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            partition_granularity (str): Partition granularity (e.g., 'day', 'hour', 'minute').
        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name= os.getenv('AWS_DEFAULT_REGION_ATHENA')
        )
        self.athena_client = boto3.client(
            "athena",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name= os.getenv('AWS_DEFAULT_REGION_ATHENA')
        )
        self.s3_bucket_name = s3_bucket_name
        self.athena_database = athena_database
        self.partition_granularity = partition_granularity
        self.column_mapping = {}  # Stores original to sanitized column names

        logger.info(f"S3DataInjector initialized for bucket: {self.s3_bucket_name} with partition granularity: {self.partition_granularity}")

    
    def sanitize_table_name(self, table_name, replace_with="_slash_"):
        """Sanitize table name to replace special characters with a safe alternative."""
        return table_name.replace(" ", "_").replace("/", replace_with).lower()

    def sanitize_column_names(self, dataframe):
        """Replace special characters in column names to make them Athena-compatible, and store original names."""
        original_columns = dataframe.columns.tolist()
        sanitized_columns = [
            col.replace(" ", "_").replace("/", "_slash_").lower().replace('*', '_star_') for col in original_columns
        ]
        self.column_mapping = dict(zip(original_columns, sanitized_columns))
        dataframe.columns = sanitized_columns
        return dataframe

    def generate_schema_definition(self, dataframe):
        """Generate schema definition for Athena based on DataFrame dtypes and partition granularity."""
        dtype_mapping = {
            'int64': 'BIGINT',
            'float64': 'DOUBLE',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TIMESTAMP',
            'object': 'STRING'
        }
        
        schema = []
        for column, dtype in dataframe.dtypes.items():
            # Explicitly set `prediction` to BOOLEAN, regardless of its inferred type
            if column.lower() == "anomaly":
                athena_type = 'BOOLEAN'
            else:
                athena_type = dtype_mapping.get(str(dtype), 'STRING')
            escaped_column = f'"{column}"' if " " in column or "/" in column else column
            schema.append(f"{escaped_column} {athena_type}")
        
        partition_columns = {
            "day": "year STRING, month STRING, day STRING",
            "hour": "year STRING, month STRING, day STRING, hour STRING",
            "minute": "year STRING, month STRING, day STRING, hour STRING, minute STRING"
        }
        
        schema_definition = ",\n".join(schema)
        logger.info(f"Schema generated: {schema_definition}")
        return schema_definition, partition_columns[self.partition_granularity]


    def generate_s3_path(self, table_name, year, month, day, hour=0, minute=0, use_full_s3_path=False):
        """
        Generate S3 path for the given table and partition values.

        Args:
            table_name (str): Table name for the data.
            year (int): Year for the partition.
            month (int): Month for the partition.
            day (int): Day for the partition.
            hour (int): Hour for the partition (optional).
            minute (int): Minute for the partition (optional).
            use_full_s3_path (bool): Whether to generate a full S3 path or a relative path.

        Returns:
            str: Generated S3 path.
        """
        sanitized_table_name = self.sanitize_table_name(table_name)
        relative_path = f"tables/{sanitized_table_name}/year={year}/month={int(month):02d}/day={int(day):02d}"
        if self.partition_granularity in ["hour", "minute"]:
            relative_path += f"/hour={int(hour):02d}"
        if self.partition_granularity == "minute":
            relative_path += f"/minute={int(minute):02d}"

        if use_full_s3_path:
            return f"s3://{self.s3_bucket_name}/{relative_path}"
        return relative_path



    def upload_dataframe_to_s3(self, dataframe, table_name):
        """
        Convert DataFrame to JSON and upload to S3 efficiently using streams and concurrent uploads.
        """
        dataframe['time'] = pd.to_datetime(dataframe['time'])  # Ensure `time` is in datetime format

        grouping = {
            "day": [dataframe['time'].dt.date],
            "hour": [dataframe['time'].dt.date, dataframe['time'].dt.hour],
            "minute": [dataframe['time'].dt.date, dataframe['time'].dt.hour, dataframe['time'].dt.minute]
        }[self.partition_granularity]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for timestamp, group in dataframe.groupby(grouping):
                date = timestamp[0]
                year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")
                hour, minute = (timestamp[1], timestamp[2]) if self.partition_granularity == "minute" else \
                            (timestamp[1], 0) if self.partition_granularity == "hour" else (0, 0)

                # Generate the relative path for S3 upload
                relative_path = self.generate_s3_path(table_name, year, month, day, hour, minute, use_full_s3_path=False)
                file_name = "data.json"  # Use a fixed file name for data injection

                json_buffer = io.StringIO()
                group.to_json(json_buffer, orient="records", lines=True)

                futures.append(
                    executor.submit(
                        self.s3_client.put_object,
                        Bucket=self.s3_bucket_name,
                        Key=f"{relative_path}/{file_name}",
                        Body=json_buffer.getvalue()
                    )
                )

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error during file upload: {e}")
                    raise e  # Ensure uploads are successful before proceeding.

        logger.info("All files uploaded successfully.")



    def create_athena_table(self, table_name, dataframe):
        """Create Athena table with specified schema and partitioning based on granularity."""
        dataframe = self.sanitize_column_names(dataframe)
        schema_definition, partition_definition = self.generate_schema_definition(dataframe)
        sanitized_table_name = self.sanitize_table_name(table_name)
        s3_path = f"s3://{self.s3_bucket_name}/tables/{sanitized_table_name}/"

        query = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {self.athena_database}.{sanitized_table_name} (
            {schema_definition}
        )
        PARTITIONED BY ({partition_definition})
        ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
        LOCATION '{s3_path}'
        TBLPROPERTIES ('classification' = 'json');
        """
        logger.info(f"Creating Athena table with query: {query}")
        self.run_athena_query(query)
        logger.info(f"Table {sanitized_table_name} created in Athena with JSON SerDe and properties.")

    def add_partition(self, table_name, partitions):
        """
        Add partitions to the Athena table in batches for faster execution.

        Args:
            table_name (str): The name of the Athena table.
            partitions (dict): A dictionary where keys are partition specs and values are S3 paths.
        """
        sanitized_table_name = self.sanitize_table_name(table_name)
        batch_size = 25  # Number of partitions per batch
        partition_items = list(partitions.items())

        for i in range(0, len(partition_items), batch_size):
            batch = partition_items[i:i + batch_size]

            # Properly format partition additions
            partition_queries = [
                f"PARTITION ({partition_spec}) LOCATION '{s3_path}'"
                for partition_spec, s3_path in batch
            ]
            
            batch_query = " ".join(partition_queries)
            
            # Add partitions query
            query = f"""
            ALTER TABLE {self.athena_database}.{sanitized_table_name}
            ADD {batch_query};
            """
            
            try:
                self.run_athena_query(query)
                logger.info(f"Batch of partitions added successfully: {len(batch)} partitions.")
            except Exception as e:
                logger.error(f"Error adding batch of partitions: {e}")
                raise e




    def run_athena_query(self, query):
        """Execute a query in Athena."""
        response = self.athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': self.athena_database},
            ResultConfiguration={'OutputLocation': f"s3://{self.s3_bucket_name}/athena/results/"}
        )
        return response['QueryExecutionId']

    def inject_data(self, dataframe, table_name):
        """Upload JSON data, create table, add partitions based on granularity."""
        dataframe.columns = [col.strip().lower() for col in dataframe.columns]
        if 'time' not in dataframe.columns:
            raise KeyError("The dataframe does not contain a 'time' column.")

        dataframe['time'] = pd.to_datetime(dataframe['time'])
        dataframe = self.sanitize_column_names(dataframe)

        # Upload data to S3 using relative paths
        self.upload_dataframe_to_s3(dataframe, table_name)

        # Create Athena table
        self.create_athena_table(table_name, dataframe)

        # Prepare partitions
        partitions = {}
        if self.partition_granularity == "minute":
            unique_minutes = dataframe['time'].dt.strftime("%Y-%m-%d %H:%M").unique()
            for minute_str in unique_minutes:
                date_part, time_part = minute_str.split(" ")
                year, month, day = date_part.split("-")
                hour, minute = time_part.split(":")
                partition_spec = f"year='{year}', month='{month}', day='{day}', hour='{hour}', minute='{minute}'"
                s3_path = self.generate_s3_path(table_name, year, month, day, hour, minute, use_full_s3_path=True)
                partitions[partition_spec] = s3_path

        # Add partitions using full S3 paths
        self.add_partition(table_name, partitions)
        return dataframe



# if __name__ == "__main__":
#     s3_bucket_name = "anomaly-detection-bucket-cloudbuilders"
#     athena_database = "athena_database"
#     table_name = "express_GET__slash_io_task_prediction"

#     file_path = r'C:\Users\Admin\Documents\Projects\CBT_VISTA\Backend_data\cbt_vista_backend-\injection_data\express_GET__slash_io_task_prediction.csv'
    
#     df = pd.read_csv(file_path)

#     injector = S3DataInjector(
#         s3_bucket_name, athena_database, aws_access_key_id, aws_secret_access_key, partition_granularity="minute"
#     )
#     result_df = injector.inject_data(df, table_name)
#     print(result_df)
#     print("Data injection complete.")
