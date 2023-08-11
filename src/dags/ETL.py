from airflow import DAG
from airflow.utils import timezone
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import timedelta, datetime
from pymongo import MongoClient
import os
import pandas as pd
import logging
import google.cloud.storage as gcs
import gcsfs
from google.cloud import bigquery

# env contains the confidential variables
MONGODB_USERNAME = os.environ["MONGODB_USERNAME"]
MONGODB_PASSWORD = os.environ["MONGODB_PASSWORD"]
BUCKET_NAME = os.environ["GCP_BUCKET"]
PROJECT_ID = os.environ["PROJECT_ID"]
CREDENTIALS_PATH = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
DATASET_NAME = os.environ["DATASET_NAME"]

def _extract(
        destination_blob_name: str = "data.parquet",
        credentials_path: str = CREDENTIALS_PATH
    ):
    logging.info("Extracting data from source")
    # Connect to MongoDB ref: https://www.mongodb.com/languages/python
    CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster0.ofns0fq.mongodb.net/"

    client = MongoClient(CONNECTION_STRING)

    db = client["sample_analytics"]

    collection = db["transactions"]

    data = collection.find()

    df = pd.DataFrame(data)

    df['_id'] = df['_id'].astype(str)

    # denormalize data******
    denormalized_df = pd.json_normalize(
        df.to_dict('records'), 
        meta=['_id', 'account_id', 'transaction_count', 'bucket_start_date', 'bucket_end_date'], 
        record_path='transactions'
    )

    # sort columns
    sorted_col = list(df.columns) + list(df['transactions'][0][0].keys())
    sorted_col_denorm_df = denormalized_df.reindex(axis=1, labels=sorted_col).drop(columns=['transactions'])

    sorted_col_denorm_df.to_parquet(destination_blob_name)

    # Load data to GCP Bucket (Data Lake)
    storage_client = gcs.Client.from_service_account_json(credentials_path)
    
    bucket = storage_client.bucket(BUCKET_NAME)
    
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(destination_blob_name)

    # remove created csv file from local
    os.remove(destination_blob_name)

    logging.info(f"Extracted data from source as {destination_blob_name}")

def _transform():
    logging.info("Transforming data")
    
    # authenticate to GCP with gcfs
    fs = gcsfs.GCSFileSystem(project=PROJECT_ID, token=CREDENTIALS_PATH)
    
    # open the file and read it into a pandas dataframe
    with fs.open(f"{BUCKET_NAME}/data.parquet", 'rb') as f:
        df = pd.read_parquet(f)
    
    # normalize data
    table_1 = df[['_id', 'account_id', 'transaction_count', 'bucket_start_date', 'bucket_end_date']]
    table_2 = df[['_id', 'date', 'amount', 'transaction_code', 'symbol', 'price', 'total']]

    # save to parquet
    table_1.to_parquet('table_DIM.parquet')
    table_2.to_parquet('table_FACT.parquet')

    # load data to GCP Bucket (Staging Area)
    destination_file_DIM = "table_DIM.parquet"
    destination_file_FACT = "table_FACT.parquet"
    fs.put(destination_file_DIM, f"{BUCKET_NAME}/staging_area/{destination_file_DIM}")
    fs.put(destination_file_FACT, f"{BUCKET_NAME}/staging_area/{destination_file_FACT}")

    # Optionally, delete the local downloaded data file
    os.remove(destination_file_DIM)
    os.remove(destination_file_FACT)
    logging.info("Transformed data and loaded to staging area")

def _load():
    logging.info("Loading data to destination")
    # Construct a BigQuery client object.
    client = bigquery.Client.from_service_account_json(CREDENTIALS_PATH)
    
    # define path
    dataset_name = DATASET_NAME
    table_name_dim = "transactions_DIM"
    table_name_fact = "transactions_FACT"
    
    # TODO(developer): Set table_id to the ID of the table to create.
    table_dim_id = f"{PROJECT_ID}.{dataset_name}.{table_name_dim}"
    table_fact_id = f"{PROJECT_ID}.{dataset_name}.{table_name_fact}"
    
    job_config = bigquery.LoadJobConfig(
        # uncomment to overwrite the table.
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.PARQUET,
    )
    uri_dim = f"gs://{BUCKET_NAME}/staging_area/table_DIM.parquet"
    uri_fact = f"gs://{BUCKET_NAME}/staging_area/table_FACT.parquet"

    # load dim table
    load_job = client.load_table_from_uri(
        uri_dim, table_dim_id, job_config=job_config
    )  # Make an API request.

    # load fact table
    load_job = client.load_table_from_uri(
        uri_fact, table_fact_id, job_config=job_config
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.

    destination_table_dim = client.get_table(table_dim_id)
    destination_table_fact = client.get_table(table_fact_id)

    logging.info("Loaded {} rows to {}.".format(destination_table_dim.num_rows, table_name_dim))
    logging.info("Loaded {} rows to {}.".format(destination_table_fact.num_rows, table_name_fact))

def _clear_staging():
    logging.info("Clearing staging area")
    """Deletes a blob from the bucket."""
    bucket_name = BUCKET_NAME

    storage_client = gcs.Client.from_service_account_json(CREDENTIALS_PATH)

    bucket = storage_client.bucket(bucket_name)
    
    blobs = bucket.list_blobs(prefix="staging_area")

    for blob in blobs:
        blob.delete()

    logging.info(f"All blobs in staging area are deleted.")

default_args ={
    "owner": "Patcharanat (Ken) :D",
    # "retries": 3,
    "retry_delay": timedelta(minutes=1),
    "schedule_interval": None,
    # "schedule_interval": "@daily", # daily transactions
    # "start_date": datetime(2023, 8, 17),
    "start_date": timezone.datetime(2023, 8, 11)
}

with DAG(
    "ETL_TD_Tech",
    default_args=default_args,
    description="Demo ETL pipeline for TD Tech assignment",
) as dag:
    
    extract = PythonOperator(
        task_id="extract",
        python_callable=_extract,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=_transform,
    )

    # sanitize = BashOperator(
    #     task_id="sanitization_production",
    #     bash_command="python src/dags/text_sanitizer.py source.txt target.txt",
    # )

    load = PythonOperator(
        task_id="load",
        python_callable=_load,
    )

    clear_staging = PythonOperator(
        task_id="clear_staging",
        python_callable=_clear_staging,
    )

    extract >> transform >> load >> clear_staging
    # sanitize >> load