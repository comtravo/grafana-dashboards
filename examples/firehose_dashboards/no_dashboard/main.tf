provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/firehose/"

  enable = false
  grafana_configuration = {
    environment          = "prod"
    influxdb_data_source = "prod"
    folder               = null
  }
}

output "op" {
  value = module.dashboard.output
}
