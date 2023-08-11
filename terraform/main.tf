# ref: https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build
terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file("../td_service_account.json")
}

resource "google_storage_bucket" "td_bucket" {
 name          = var.bucket
 location      = var.region
 storage_class = "STANDARD"

 uniform_bucket_level_access = true
 
 force_destroy = true
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = var.dataset_id
  location                    = var.region
}

resource "google_bigquery_table" "table_DIM" {
  dataset_id  = google_bigquery_dataset.dataset.dataset_id
  table_id    = "transactions_DIM"
  deletion_protection = false
  schema = <<EOF
    [
      {
        "name": "_id",
        "type": "STRING"
      },
      {
        "name": "account_id",
        "type": "STRING"
      },
      {
        "name": "transaction_count",
        "type": "INTEGER"
      },
      {
        "name": "bucket_start_date",
        "type": "TIMESTAMP"
      },
      {
        "name": "bucket_end_date",
        "type": "TIMESTAMP"
      }
    ]
  EOF
}

resource "google_bigquery_table" "table_FACT" {
  dataset_id  = google_bigquery_dataset.dataset.dataset_id
  table_id    = "transactions_FACT"
  deletion_protection = false
  schema = <<EOF
    [
      {
        "name": "_id",
        "type": "STRING"
      },
      {
        "name": "date",
        "type": "TIMESTAMP"
      },
      {
        "name": "amount",
        "type": "INTEGER"
      },
      {
        "name": "transaction_code",
        "type": "STRING"
      },
      {
        "name": "symbol",
        "type": "STRING"
      },
      {
        "name": "price",
        "type": "STRING"
      },
      {
        "name": "total",
        "type": "STRING"
      }
    ]
  EOF
}
