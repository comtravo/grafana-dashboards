provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../"

  enable = false
  grafana_configuration = {
    name = var.name
    environment = "prod"
    data_source = "prod"
    alert = false
    service = "lambda"
    trigger = "cron"
  }
}

output "op" {
  value = module.dashboard
}
