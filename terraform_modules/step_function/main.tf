terraform {
  required_version = ">= 0.12"
  required_providers {
    grafana = {
      source = "grafana/grafana"
    }
    local = {
      source = "hashicorp/local"
    }
    null = {
      source = "hashicorp/null"
    }
  }
}


variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    arn                    = string
    environment            = string
    cloudwatch_data_source = string
    influxdb_data_source   = string
    notifications          = list(string)
    lambdas                = list(string)
    folder                 = string
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  notification_args = try(length(var.grafana_configuration.notifications), 0) > 0 ? "--notifications ${join(" ", var.grafana_configuration.notifications)}" : ""
  lambda_args       = try(length(var.grafana_configuration.lambdas), 0) > 0 ? "--lambdas ${join(" ", var.grafana_configuration.lambdas)}" : ""
  dahboard_path     = "${path.module}/dashboard.json"
}

resource "null_resource" "generate_dashboard" {

  count = var.enable ? 1 : 0

  provisioner "local-exec" {
    command = "python3 ${path.module}/../../bin.py --name ${var.grafana_configuration.arn} --environment ${var.grafana_configuration.environment} ${local.notification_args} --influxdb_data_source ${var.grafana_configuration.influxdb_data_source} --cloudwatch_data_source ${var.grafana_configuration.cloudwatch_data_source} step-function ${local.lambda_args} | json_pp > ${local.dahboard_path}"
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
