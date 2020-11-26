## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| grafana | n/a |
| local | n/a |
| null | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| grafana_configuration | Configuration for creating Grafana dashboards and alerts | <pre>object({<br>    name        = string<br>    environment = string<br>    data_source = string<br>    trigger     = string<br>    alert       = bool<br>    topics      = list(string)<br>    folder      = string<br>  })</pre> | n/a | yes |
| enable | true to enable the module | `bool` | `false` | no |

## Outputs

| Name | Description |
|------|-------------|
| output | n/a |

