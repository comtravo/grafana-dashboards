provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/lambda/triggers/generic"

  enable = true
  grafana_configuration = {
    name                   = var.name
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    trigger                = "cloudwatch-event-schedule"
    notifications          = ["slack"]
    folder                 = null
    topics                 = null
  }
}

output "op" {
  value = module.dashboard.output
}
