variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    name          = string
    environment   = string
    data_source   = string
    folder        = string
    engine        = string
    notifications = list(string)
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  dahboard_path     = "${path.module}/dashboard.json"
  notification_args = length(var.grafana_configuration.notifications) > 0 ? "--notifications ${join(" ", var.grafana_configuration.notifications)}" : ""
}

resource "null_resource" "generate_dashboard" {

  count = var.enable ? 1 : 0

  provisioner "local-exec" {
    command = "python3 ${path.module}/../../bin.py --name ${var.grafana_configuration.name} ${local.notification_args} --environment ${var.grafana_configuration.environment} --data_source ${var.grafana_configuration.data_source} rds --engine ${var.grafana_configuration.engine} | json_pp > ${local.dahboard_path}"
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

output "output" {
  description = "Grafana slug and dashboard_id"
  value = {
    slug         = try(grafana_dashboard.this[0].slug, "")
    dashboard_id = try(grafana_dashboard.this[0].dashboard_id, "")
  }
}
