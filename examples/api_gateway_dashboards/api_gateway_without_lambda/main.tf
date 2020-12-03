provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/api_gateway/"

  enable = true
  grafana_configuration = {
    name          = var.name
    environment   = "prod"
    data_source   = "prod"
    notifications = ["slack"]
    folder        = null
    lambdas       = []
  }
}

output "op" {
  value = module.dashboard.output
}
