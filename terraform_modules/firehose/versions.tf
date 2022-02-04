terraform {
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
  required_version = "~> 1.1.0"
}
