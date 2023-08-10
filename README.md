# TD Tech

by: Patcharanat P.

The answers are coresponding to the following questions:

## Question 1: Data Pipeline design

1. Setting up airflow containers, involving the following files:
    - [docker-compose.yml](./docker-compose.yml)
    - [Dockerfile](./Dockerfile)
    - [fernet_key_generator.py](./fernet_key_generator.py)
    - [fernet-key.txt](./fernet-key.txt)

2. Install dependencies
    - [requirements.txt](./requirements.txt)

3. Setting up GCP Infrastructure by Terraform
    - [main.tf](./terraform/main.tf)
    - [variables.tf](./terraform/variables.tf)

4. Setting up airflow DAGs
    - [ETL.py](./src/dags/ETL.py)

5. Data modeling for handling semi-structured demo data from MongoDB
    - [data_modeling.ipynb](./data_modeling.ipynb)

***Note: To run the demo, please follow the steps below:***
1. Create a new cluster0 (free tier) in MongoDB Atlas
2. create `.env` file containing:
```
MONGODB_USERNAME='mongo_username'
MONGODB_PASSWORD='mongo_password'
```
3. Create a new project in GCP
4. Create a new service account in GCP
5. Download the service account key as `service_account.json` and put it in the root directory
6. Add the following roles to the service account:
    - BigQuery Admin
    - BigQuery Data Editor
    - BigQuery Data Viewer
    - BigQuery Job User
    - BigQuery User
    - Storage Admin
    - Storage Object Admin
    - Storage Object Creator
    - Storage Object Viewer
7. Run the following commands:
```bash
terraform init

terraform plan

terraform apply

# wait for the terraform to finish

# can omit building images part
docker compose build

docker compose up -d

# wait for the airflow init to finish and airflow webserver to be ready

# go to `localhost:8080`

# trigger the DAG

# check data in gcp bigquery and bigquery

# when you're done with demo
docker compose down -v

# delete built images in docker desktop

terraform destroy
```

## Question 2: Text Sanitizer

The script written in [text_sanitizer.py](./src/dags/text_sanitizer.py) as OOP Python can be run by the following cli command:

```bash
# without arguments (plus user interactive input)
python text_sanitizer.py

# or with arguments
python text_sanitizer.py source.txt target.txt True
# input cli: python3 text_sanitizer.py source target write_out

# use this if run the script in the project root directory
python ./src/dags/text_sanitizer.py
```

involving the following files:
- [text_sanitizer.py](./src/dags/text_sanitizer.py)
- [source.txt](./src/dags/source.txt)
- [target.txt](./src/dags/target.txt)

## Question 3: SQL

The SQL query is written in [sql_query.sql](./sql_query.sql)