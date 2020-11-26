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

  source = "../../"

  enable = true
  dashboard_configuration = {
    name        = var.name
    environment = "prod"
    data_source = "prod"
    alert       = false
    service     = "lambda"
    folder      = grafana_folder.this.id
  }
  lambda_configuration = {
    trigger = "cron"
  }
}

output "op" {
  value = module.dashboard.output
}
