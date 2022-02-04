## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_external"></a> [external](#provider\_external) | n/a |
| <a name="provider_grafana"></a> [grafana](#provider\_grafana) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [grafana_dashboard.this](https://registry.terraform.io/providers/grafana/grafana/latest/docs/resources/dashboard) | resource |
| [external_external.dashboard](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_enable"></a> [enable](#input\_enable) | true to enable the module | `bool` | `false` | no |
| <a name="input_grafana_configuration"></a> [grafana\_configuration](#input\_grafana\_configuration) | Configuration for creating Grafana dashboards and alerts | <pre>object({<br>    name                   = string<br>    environment            = string<br>    cloudwatch_data_source = string<br>    fifo                   = bool<br>    notifications          = list(string)<br>    topics                 = list(string)<br>    folder                 = string<br>  })</pre> | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_output"></a> [output](#output\_output) | Grafana slug and dashboard\_id |
