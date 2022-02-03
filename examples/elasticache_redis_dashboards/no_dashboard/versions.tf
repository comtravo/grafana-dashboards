required_version = "~> 1.1.5"required_version = "~> 1.1.5"terraform {
  required_providers {
    grafana = {
      source = "grafana/grafana"
    }
  }
  required_version = ">= 0.14"
}
