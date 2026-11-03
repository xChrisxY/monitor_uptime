terraform {

  # versión mínima de Terraform
  required_version = ">= 1.0"

  # Los proveedores que vamos a usar
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }

  }

}

# Provider de AWS
provider "aws" {

  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = "demo"
      ManagedBy   = "Terraform"
    }

  }

}

# Información de la cuenta actual
data "aws_caller_identity" "current" {}

# Información de la región actual
data "aws_region" "current" {}

