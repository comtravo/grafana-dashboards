provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

variable "name" {
  type = string
}


resource "grafana_alert_notification" "slack_1" {
  name          = "${var.name}-slack_1"
  type          = "slack"
  is_default    = false
  send_reminder = true
  frequency     = "24h"

  settings = {
    recipient      = "#lorem"
    username       = "bot"
    mentionChannel = "channel"
    token          = "vdssvbdshjvbdskbvkdbv"
    iconEmoji      = ":ghost:"
    url            = "http://slack"
    uploadImage    = false
  }
}

resource "grafana_alert_notification" "slack_2" {
  name          = "${var.name}-slack_2"
  type          = "slack"
  is_default    = false
  send_reminder = true
  frequency     = "24h"

  settings = {
    recipient      = "#lorem"
    username       = "bot"
    mentionChannel = "channel"
    token          = "vdssvbdshjvbdskbvkdbv"
    iconEmoji      = ":ghost:"
    url            = "http://slack"
    uploadImage    = false
  }
}

module "dashboard" {

  source = "../../../terraform_modules/elasticache_redis/"

  enable = true
  grafana_configuration = {
    name                   = "es"
    cache_cluster_id       = "1234567890"
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    folder                 = null
    notifications          = [grafana_alert_notification.slack_1.uid, grafana_alert_notification.slack_2.uid]
  }
}

output "op" {
  value = module.dashboard.output
}
