terraform {
  required_version = ">= 0.13"
  required_providers {
    grafana = {
      source = "grafana/grafana"
    }
    local = {
      source = "hashicorp/local"
    }
    null = {
      source = "hashicorp/null"
    }
  }
}
