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
    name                   = var.name
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    influxdb_data_source   = "influxdb"
    trigger                = "sns"
    notifications          = ["slack"]
    folder                 = null
    topics                 = ["topic-1", "topic-2", "topic-3"]
  }
}

output "op" {
  value = module.dashboard.output
}
