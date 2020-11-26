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
  dashboard_configuration = {
    name        = var.name
    environment = "prod"
    data_source = "prod"
    alert       = false
    service     = "lambda"
    folder      = null
  }
  lambda_configuration = {
    trigger = "cron"
  }
}

output "op" {
  value = module.dashboard.output
}
