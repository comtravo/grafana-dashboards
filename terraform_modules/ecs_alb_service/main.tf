variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    name                      = string
    environment               = string
    cloudwatch_data_source    = string
    elasticsearch_data_source = string
    lucene_query              = string
    notifications             = list(string)
    folder                    = string
    cluster_name              = string
    max                       = number
    loadbalancer              = string
    target_group              = string
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  elasticsearch_data_source_args = var.grafana_configuration.elasticsearch_data_source == null ? [] : ["--es", var.grafana_configuration.elasticsearch_data_source]
  lucene_query_args              = var.grafana_configuration.lucene_query == null ? [] : ["--lucene-query", var.grafana_configuration.lucene_query]
  notification_args              = try(length(var.grafana_configuration.notifications), 0) > 0 ? flatten(["--notifications", var.grafana_configuration.notifications]) : []
}

data "external" "dashboard" {
  count = var.enable ? 1 : 0
  program = flatten([
    "python3", "${path.module}/../../bin.py",
    "--name", var.grafana_configuration.name,
    "--environment", var.grafana_configuration.environment,
    local.notification_args,
    "--cw", var.grafana_configuration.cloudwatch_data_source,
    local.elasticsearch_data_source_args,
    local.lucene_query_args,
    "ecs-alb-service",
    "--cluster-name", var.grafana_configuration.cluster_name,
    "--max", var.grafana_configuration.max,
    "--loadbalancer", var.grafana_configuration.loadbalancer,
    "--target-group", var.grafana_configuration.target_group,
  ])
}


resource "grafana_dashboard" "this" {
  count       = var.enable ? 1 : 0
  folder      = var.grafana_configuration.folder
  config_json = base64decode(data.external.dashboard[0].result.base64EncodedJson)
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
