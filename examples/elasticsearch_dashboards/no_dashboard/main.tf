provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/elasticsearch/"

  enable = false
  grafana_configuration = {
    environment   = "prod"
    data_source   = "prod"
    folder        = null
    notifications = []
  }
}

output "op" {
  value = module.dashboard.output
}
