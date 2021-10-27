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

  source = "../../../terraform_modules/elasticsearch/"

  enable = true
  grafana_configuration = {
    name                   = "es"
    client_id              = "1234567890"
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    folder                 = grafana_folder.this.id
    notifications          = []
  }
}

output "op" {
  value = module.dashboard.output
}
