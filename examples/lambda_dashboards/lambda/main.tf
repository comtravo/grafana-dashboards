provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/lambda/"

  enable = true
  grafana_configuration = {
    name          = var.name
    environment   = "prod"
    data_source   = "prod"
    trigger       = "cron"
    notifications = ["slack"]
    folder        = null
    topics        = []
  }
}

output "op" {
  value = module.dashboard.output
}
