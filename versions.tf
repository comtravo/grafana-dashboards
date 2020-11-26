terraform {
  required_version = ">= 0.12"
  required_providers {
    grafana = "~> 1.7"
  }
  experiments = [variable_validation]
}
