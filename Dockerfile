FROM apache/airflow:slim-2.6.2-python3.10

# WORKDIR /app

COPY requirements.txt .

COPY td_service_account.json .

RUN pip install --no-cache-dir -r requirements.txt