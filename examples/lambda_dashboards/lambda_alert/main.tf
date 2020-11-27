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
    name        = var.name
    environment = "prod"
    data_source = "prod"
    trigger     = "cron"
    alert       = true
    folder      = null
    topics      = []
  }
}

output "op" {
  value = module.dashboard.output
}
