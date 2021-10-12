## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13 |
| <a name="requirement_grafana"></a> [grafana](#requirement\_grafana) | ~> 1.7 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_grafana"></a> [grafana](#provider\_grafana) | ~> 1.7 |
| <a name="provider_local"></a> [local](#provider\_local) | n/a |
| <a name="provider_null"></a> [null](#provider\_null) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [grafana_dashboard.this](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [null_resource.generate_dashboard](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [local_file.dashboard](https://registry.terraform.io/providers/hashicorp/local/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_enable"></a> [enable](#input\_enable) | true to enable the module | `bool` | `false` | no |
| <a name="input_grafana_configuration"></a> [grafana\_configuration](#input\_grafana\_configuration) | Configuration for creating Grafana dashboards and alerts | <pre>object({<br>    name                   = string<br>    environment            = string<br>    cloudwatch_data_source = string<br>    influxdb_data_source   = string<br>    trigger                = string<br>    notifications          = list(string)<br>    topics                 = list(string)<br>    folder                 = string<br>  })</pre> | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_output"></a> [output](#output\_output) | Grafana slug and dashboard\_id |
