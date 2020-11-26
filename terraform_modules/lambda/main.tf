variable "grafana_configuration" {
  description = "Configuration for creating Grafana dashboards and alerts"
  type = object({
    name        = string
    environment = string
    data_source = string
    trigger     = string
    alert       = bool
    topics      = list(string)
  })
}

variable "enable" {
  description = "true to enable the module"
  default     = false
}

locals {
  alert_flag  = var.grafana_configuration.alert ? "--alert" : ""
  topics_args = length(var.grafana_configuration.topics) > 0 ? "--topics ${var.grafana_configuration.topics}" : ""
}

resource "null_resource" "generate_dashboard" {

  count = var.enable ? 1 : 0

  provisioner "local-exec" {
    working_dir = path.module
    command     = "python bin.py --name ${var.grafana_configuration.name} --environment ${var.grafana_configuration.environment}  --data_source ${var.grafana_configuration.data_source} ${local.alert_flag} lambda ${var.grafana_configuration.data_source} ${local.topics_args} > tmp/dashboard.json"
  }

  triggers = {
    always = timestamp()
  }
}

output "id" {
  description = "null resource id"
  value       = try(null_resource.generate_dashboard[0].id, "")
}
