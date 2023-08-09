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
  credentials = file("credentials.json")
}

resource "google_storage_bucket" "td_bucket" {
 name          = var.bucket
 location      = var.region
 storage_class = "STANDARD"

 uniform_bucket_level_access = true
}

resource "bq_dataset" "td_dataset" {
  dataset_id = "td_dataset"
  location = var.region
}