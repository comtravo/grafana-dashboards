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

  source = "../../../terraform_modules/api_gateway/"

  enable = true
  grafana_configuration = {
    name          = var.name
    environment   = "prod"
    data_source   = "prod"
    notifications = ["slack"]
    folder        = grafana_folder.this.id
    lambdas       = ["lambda-1", "lambda-2"]
  }
}

output "op" {
  value = module.dashboard.output
}
