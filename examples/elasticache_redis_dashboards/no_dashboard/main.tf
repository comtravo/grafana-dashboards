provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}

module "dashboard" {

  source = "../../../terraform_modules/elasticache_redis/"

  enable = false
  grafana_configuration = {
    name                   = "es"
    cache_cluster_id       = "1234567890"
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    influxdb_data_source   = "influxdb"
    folder                 = null
    notifications          = []
  }
}

output "op" {
  value = module.dashboard.output
}
