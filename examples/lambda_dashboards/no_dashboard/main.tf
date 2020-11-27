provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/lambda/"

  enable = false
  grafana_configuration = {
    name        = var.name
    environment = "prod"
    data_source = "prod"
    trigger     = "cron"
    alert       = false
    folder      = null
    topics      = []
  }
}

output "op" {
  value = module.dashboard.output
}
