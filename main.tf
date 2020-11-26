variable "enable" {
  description = "Enable creating dashboards"
  type        = bool
  default     = false
}

variable "dashboard_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  default     = null
  type = object({
    name        = string
    environment = string
    data_source = string
    service     = string
    alert       = bool
    folder      = string
  })
}
variable "lambda_configuration" {
  description = "Configuration for creating lambda dashboards and alerts"
  type        = any
  default = {
    trigger = ""
    topics  = []
  }
}

module "generate_lambda_dashboard" {
  source = "./terraform_modules/lambda/"

  enable = var.dashboard_configuration.service == "lambda" && var.enable ? true : false
  grafana_configuration = {
    name        = var.dashboard_configuration.name
    environment = var.dashboard_configuration.environment
    data_source = var.dashboard_configuration.data_source
    alert       = var.dashboard_configuration.alert
    folder      = var.dashboard_configuration.folder
    trigger     = var.lambda_configuration.trigger
    topics      = try(var.lambda_configuration.topics, [])
  }
}
