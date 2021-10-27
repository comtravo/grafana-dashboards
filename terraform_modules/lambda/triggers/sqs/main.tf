variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    name                   = string
    environment            = string
    cloudwatch_data_source = string
    fifo                   = bool
    notifications          = list(string)
    topics                 = list(string)
    folder                 = string
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  notification_args = try(length(var.grafana_configuration.notifications), 0) > 0 ? flatten(["--notifications", var.grafana_configuration.notifications]) : []
  topics_args       = try(length(var.grafana_configuration.topics), 0) > 0 ? flatten(["--topics", var.grafana_configuration.topics]) : []
  trigger           = try(length(var.grafana_configuration.topics), 0) > 0 ? "sns" : "sqs"
  fifo_args         = var.grafana_configuration.fifo == true ? ["--fifo"] : []
}

data "external" "dashboard" {
  program = flatten([
    "python3",
    "${path.module}/../../../../bin.py",
    "--name",
    var.grafana_configuration.name,
    "--environment",
    var.grafana_configuration.environment,
    local.notification_args,
    "--cloudwatch_data_source",
    var.grafana_configuration.cloudwatch_data_source,
    "lambda",
    local.trigger,
    local.topics_args,
    local.fifo_args
  ])
}

resource "grafana_dashboard" "this" {
  count       = var.enable ? 1 : 0
  folder      = var.grafana_configuration.folder
  config_json = base64decode(data.external.dashboard.result.base64EncodedJson)
}

output "output" {
  description = "Grafana slug and dashboard_id"
  value = {
    slug         = try(grafana_dashboard.this[0].slug, "")
    dashboard_id = try(grafana_dashboard.this[0].dashboard_id, "")
    uid          = try(grafana_dashboard.this[0].uid, "")
    version      = try(grafana_dashboard.this[0].version, "")
  }
}
