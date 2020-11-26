variable "enable" {
  description = "Enable creating dashboards"
  type = bool
  default = false
}
variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type        = any
  default     = null
}

module "generate_lambda_dashboard" {
  source = "./terraform_modules/lambda/"

  enable = var.grafana_configuration.service == "lambda" && var.enable ? true : false
  grafana_configuration = {
    name        = tostring(var.grafana_configuration.name)
    environment = tostring(var.grafana_configuration.environment)
    data_source = tostring(var.grafana_configuration.data_source)
    alert       = tobool(var.grafana_configuration.alert)
    trigger     = try(tostring(var.grafana_configuration.trigger), "")
    topics      = try(var.grafana_configuration.topics, [])
  }
}


data "local_file" "dashboard" {
  count = var.enable ? 1 : 0
  filename   = "dashboard.json"
}

resource "grafana_dashboard" "this" {
  count = var.enable ? 1 : 0
  folder      = var.grafana_configuration.folder
  config_json = data.local_file.dashboard[0].content
}
