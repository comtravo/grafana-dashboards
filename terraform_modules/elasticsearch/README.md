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
| enable | true to enable the module | `bool` | `false` | no |
| grafana\_configuration | Configuration for creating Grafana dashboards and alerts | <pre>object({<br>    environment   = string<br>    data_source   = string<br>    folder        = string<br>    notifications = list(string)<br>  })</pre> | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| output | Grafana slug and dashboard\_id |

