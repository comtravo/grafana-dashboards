provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/lambda/triggers/generic"

  enable = false
  grafana_configuration = {
    name                   = var.name
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    influxdb_data_source   = "influxdb"
    trigger                = "cloudwatch-event-schedule"
    notifications          = ["slack"]
    folder                 = null
    topics                 = []
  }
}

output "op" {
  value = module.dashboard.output
}
