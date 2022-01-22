provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/ecs_alb_service/"

  enable = false
  grafana_configuration = {
    name                      = var.name
    environment               = "prod"
    cloudwatch_data_source    = "cloudwatch"
    elasticsearch_data_source = "es"
    lucene_query              = "tag: ${var.name} AND log.level: [50 TO *]"
    notifications             = ["slack"]
    folder                    = null
    cluster_name              = "cluster-1"
    max                       = 100
    loadbalancer              = "foo"
    target_group              = "bar"
  }
}

output "op" {
  value = module.dashboard.output
}
