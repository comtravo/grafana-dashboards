variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    name        = string
    environment = string
    data_source = string
    trigger     = string
    alert       = bool
    topics      = list(string)
    folder      = string
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  alert_flag    = var.grafana_configuration.alert ? "--alert" : ""
  topics_args   = length(var.grafana_configuration.topics) > 0 ? "--topics ${var.grafana_configuration.topics}" : ""
  dahboard_path = "${path.cwd}/dashboard.json"
}

resource "null_resource" "generate_dashboard" {

  count = var.enable ? 1 : 0

  provisioner "local-exec" {
    command = "python ${path.module}/../../bin.py --name ${var.grafana_configuration.name} --environment ${var.grafana_configuration.environment}  --data_source ${var.grafana_configuration.data_source} ${local.alert_flag} lambda ${var.grafana_configuration.trigger} ${local.topics_args} > ${local.dahboard_path}"
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
  value = {
    slug         = try(grafana_dashboard.this[0].slug, "")
    dashboard_id = try(grafana_dashboard.this[0].dashboard_id, "")
  }
}
