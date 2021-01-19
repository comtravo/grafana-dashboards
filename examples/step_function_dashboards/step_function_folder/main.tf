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

  source = "../../../terraform_modules/step_function/"

  enable = true
  grafana_configuration = {
    arn                    = var.name
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    influxdb_data_source   = "influxdb"
    notifications          = ["slack"]
    folder                 = grafana_folder.this.id
    lambdas                = ["lambda-1", "lambda-2"]
  }
}

output "op" {
  value = module.dashboard.output
}
