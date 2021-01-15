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

  source = "../../../terraform_modules/rds/"

  enable = true
  grafana_configuration = {
    name                   = var.name
    engine                 = "postgres"
    environment            = "prod"
    cloudwatch_data_source = "cloudwatch"
    influxdb_data_source   = "influxdb"
    folder                 = null
    notifications          = [grafana_alert_notification.slack_1.uid, grafana_alert_notification.slack_2.uid]
  }
}

output "op" {
  value = module.dashboard.output
}
