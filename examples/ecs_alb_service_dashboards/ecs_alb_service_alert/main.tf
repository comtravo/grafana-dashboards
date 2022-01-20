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

  source = "../../../terraform_modules/ecs_alb_service/"

  enable = true

  grafana_configuration = {
    name                      = var.name
    environment               = "prod"
    cloudwatch_data_source    = "cloudwatch"
    elasticsearch_data_source = "es"
    lucene_query              = "tag: ${var.name} AND log.level: [50 TO *]"
    notifications             = [grafana_alert_notification.slack_1.id, grafana_alert_notification.slack_2.id]
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
