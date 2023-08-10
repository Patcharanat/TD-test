from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import timedelta, datetime
from pymongo import MongoClient
import os
import pandas as pd
import google.cloud.storage as gcs
import logging

# env contains the confidential variables
MONGODB_USERNAME = os.environ.get("MONGODB_USERNAME")
MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD")
GCP_BUCKET = "TD_BUCKET"
credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

def _extract(
        destination_blob_name: str = "data.parquet", 
        gcp_bucket: str = GCP_BUCKET, 
        credentials_path: str = credentials_path
    ):
    # Connect to MongoDB ref: https://www.mongodb.com/languages/python
    CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@cluster0.ofns0fq.mongodb.net/"

    client = MongoClient(CONNECTION_STRING)

    db = client["sample_analytics"]

    collection = db["transactions"]

    data = collection.find()

    df = pd.DataFrame(data)

    df.to_parquet(destination_blob_name)

    # Load data to GCP Bucket (Data Lake)
    storage_client = gcs.Client.from_service_account_json(credentials_path)
    
    bucket = storage_client.bucket(gcp_bucket)
    
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(destination_blob_name)

    # remove created csv file from local
    os.remove(destination_blob_name)

    logging.info(f"Extracted data from source as {destination_blob_name}")

def _transform():
    print("Transforming data")

def _load():
    print("Loading data to destination")

def _clear_staging():
    print("Clearing staging area")

default_args ={
    "owner": "Patcharanat (Ken) :D",
    "retries": 3,
    "retry_delay": timedelta(minutes=3),
    "schedule_interval": "@daily", # daily transactions
    "start_date": datetime(2023, 8, 17),
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