variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    name                   = string
    environment            = string
    cloudwatch_data_source = string
    trigger                = string
    notifications          = list(string)
    folder                 = string
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  notification_args = length(var.grafana_configuration.notifications) > 0 ? "--notifications ${join(" ", var.grafana_configuration.notifications)}" : ""
  dahboard_path     = "${path.module}/dashboard.json"
}

resource "null_resource" "generate_dashboard" {

  count = var.enable ? 1 : 0

  provisioner "local-exec" {
    command = "python3 ${path.module}/../../../../bin.py --name ${var.grafana_configuration.name} --environment ${var.grafana_configuration.environment} ${local.notification_args} --cloudwatch_data_source ${var.grafana_configuration.cloudwatch_data_source} lambda ${var.grafana_configuration.trigger} > ${local.dahboard_path}"
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
    uid          = try(grafana_dashboard.this[0].uid, "")
    version      = try(grafana_dashboard.this[0].version, "")
  }
}
