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
    environment   = "prod"
    data_source   = "prod"
    folder        = grafana_folder.this.id
    notifications = []
  }
}

output "op" {
  value = module.dashboard.output
}