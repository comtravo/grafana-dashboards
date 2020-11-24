provider "grafana" {
  url  = "http://grafana:3000"
  auth = "admin:admin"
}

locals {
  sfn = {
    name = "sfn-gateway-prod"
    environment = "prod"
    data_source = "prod"
    topics = ["lambda-elasticsearch-booking-prod", "lambda-pretty-mail-payment-prod", "lambda-offer-created-prod"]
  }
}

# data "external" "sfn" {
#   working_dir = ".."
#   program = [
#     "python", "bin.py",
#     "--name", "${local.sfn.name}",
#     "--environment", "${local.sfn.environment}",
#     "--data_source", "${local.sfn.data_source}",
#     "--alert",
#     # "lambda", "sns", "--topics", "${join(" ", local.sfn.topics)}"
#     "lambda", "sns", "--topics", "lorem"
#   ]
# }

resource "null_resource" "sfn" {

  provisioner "local-exec" {
    working_dir = ".."
    command = "python bin.py --name ${local.sfn.name} --environment ${local.sfn.environment}  --data_source ${local.sfn.data_source} --alert lambda sns --topics ${join(" ", local.sfn.topics)} > terraform/dashboard.json"
  }

  triggers = {
    always = timestamp()
  }
}

data "local_file" "dashboard" {
  filename = "dashboard.json"
  depends_on = [null_resource.sfn]
}

resource "grafana_dashboard" "sfn" {
  config_json = data.local_file.dashboard.content
}



# resource "grafana_dashboard" "sfn_external" {
#   config_json = data.external.sfn.result
# }
