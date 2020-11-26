## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.12 |
| grafana | ~> 1.7 |

## Providers

No provider.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| dashboard_configuration | Configuration for creating Grafana dashboards and alerts | <pre>object({<br>    name        = string<br>    environment = string<br>    data_source = string<br>    service     = string<br>    alert       = bool<br>    folder      = string<br>  })</pre> | `null` | no |
| enable | Enable creating dashboards | `bool` | `false` | no |
| lambda_configuration | Configuration for creating lambda dashboards and alerts | `any` | <pre>{<br>  "topics": [],<br>  "trigger": ""<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| output | Dashboard output |

