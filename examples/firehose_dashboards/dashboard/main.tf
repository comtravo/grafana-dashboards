provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/firehose/"

  enable = true
  grafana_configuration = {
    environment   = "prod"
    data_source   = "prod"
    folder        = null
  }
}

output "op" {
  value = module.dashboard.output
}
