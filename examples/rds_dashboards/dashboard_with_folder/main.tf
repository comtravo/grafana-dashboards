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

  source = "../../../terraform_modules/rds/"

  enable = true
  grafana_configuration = {
    name                   = var.name
    engine                 = "mysql"
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    folder                 = grafana_folder.this.id
    notifications          = []
  }
}

output "op" {
  value = module.dashboard.output
}
