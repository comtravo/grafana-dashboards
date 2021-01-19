provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

resource "grafana_folder" "this" {
  title = "${var.name}-folder"
}

module "dashboard" {

  source = "../../../terraform_modules/lambda/"

  enable = true
  grafana_configuration = {
    name                   = var.name
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    influxdb_data_source   = "influxdb"
    trigger                = "cloudwatch-event-schedule"
    notifications          = ["slack"]
    folder                 = grafana_folder.this.id
    topics                 = []
  }
}

output "op" {
  value = module.dashboard.output
}
