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
    name        = var.name
    environment = "prod"
    data_source = "prod"
    trigger     = "sns"
    alert       = false
    folder      = null
    topics      = ["topic-1", "topic-2", "topic-3"]
  }
}

output "op" {
  value = module.dashboard.output
}
