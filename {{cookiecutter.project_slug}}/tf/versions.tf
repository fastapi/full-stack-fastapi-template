terraform {
  required_version = ">= 1.2.5, < 2.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}
