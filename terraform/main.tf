provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}




locals {
  sfn = {
    name        = "sfn-gateway-prod"
    environment = "prod"
    data_source = "prod"
    topics      = ["lambda-elasticsearch-booking-prod", "lambda-pretty-mail-payment-prod", "lambda-offer-created-prod"]
  }
  # sfn = {
  #   name        = "metabase-prod"
  #   environment = "prod"
  #   data_source = "prod"
  #   topics = [
  #     "lambda-elasticsearch-traveler-prod",
  #     "lambda-elasticsearch-company-prod",
  #     "lambda-elasticsearch-booking-prod",
  #     "lambda-offer-prod",
  #     "invoice-correction-prod"
  #   ]
  # }
}

resource "null_resource" "sfn" {

  provisioner "local-exec" {
    working_dir = ".."
    command     = "python bin.py --name ${local.sfn.name} --environment ${local.sfn.environment}  --data_source ${local.sfn.data_source} --alert lambda sns --topics ${join(" ", local.sfn.topics)} > terraform/dashboard.json"
  }

  triggers = {
    always = timestamp()
  }
}

data "local_file" "dashboard" {
  filename   = "dashboard.json"
  depends_on = [null_resource.sfn]
}

resource "grafana_dashboard" "sfn" {
  config_json = data.local_file.dashboard.content
}
