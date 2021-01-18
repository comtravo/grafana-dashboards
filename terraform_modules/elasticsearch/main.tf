variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    name                   = string
    client_id              = string
    environment            = string
    influxdb_data_source   = string
    cloudwatch_data_source = string
    folder                 = string
    notifications          = list(string)
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  dahboard_path           = "${path.module}/dashboard.json"
  alert_dahboard_path     = "${path.module}/alert_dashboard.json"
  create_alerts_dashboard = length(var.grafana_configuration.notifications) > 0 ? true : false
  notification_args       = length(var.grafana_configuration.notifications) > 0 ? "--notifications ${join(" ", var.grafana_configuration.notifications)}" : ""
}

resource "null_resource" "generate_dashboard" {

  count = var.enable ? 1 : 0

  provisioner "local-exec" {
    command = "python3 ${path.module}/../../bin.py --name ${var.grafana_configuration.name} --client_id ${var.grafana_configuration.client_id} --environment ${var.grafana_configuration.environment} --cloudwatch_data_source ${var.grafana_configuration.cloudwatch_data_source} --influxdb_data_source ${var.grafana_configuration.influxdb_data_source} elasticsearch | json_pp > ${local.dahboard_path}"
  }

  triggers = {
    always = timestamp()
  }
}

data "local_file" "dashboard" {
  count    = var.enable ? 1 : 0
  filename = local.dahboard_path

  depends_on = [null_resource.generate_dashboard]
}

resource "grafana_dashboard" "this" {
  count       = var.enable ? 1 : 0
  folder      = var.grafana_configuration.folder
  config_json = data.local_file.dashboard[0].content
}

resource "null_resource" "generate_alerts_dashboard" {

  count = var.enable && local.create_alerts_dashboard ? 1 : 0

  provisioner "local-exec" {
    command = "python3 ${path.module}/../../bin.py --name elasticsearch --environment ${var.grafana_configuration.environment} ${local.notification_args} --influxdb_data_source ${var.grafana_configuration.influxdb_data_source} elasticsearch-alerts | json_pp > ${local.alert_dahboard_path}"
  }

  triggers = {
    always = timestamp()
  }
}

data "local_file" "alerts_dashboard" {
  count    = var.enable && local.create_alerts_dashboard ? 1 : 0
  filename = local.alert_dahboard_path

  depends_on = [null_resource.generate_alerts_dashboard]
}

resource "grafana_dashboard" "alert" {
  count       = var.enable && local.create_alerts_dashboard ? 1 : 0
  folder      = var.grafana_configuration.folder
  config_json = data.local_file.alerts_dashboard[0].content
}

output "output" {
  description = "Grafana slug and dashboard_id"
  value = {
    slug = [
      try(grafana_dashboard.this[0].slug, ""),
      try(grafana_dashboard.alert[0].slug, "")
    ]
    dashboard_id = [
      try(grafana_dashboard.this[0].dashboard_id, ""),
      try(grafana_dashboard.alert[0].dashboard_id, "")
    ]
  }
}
