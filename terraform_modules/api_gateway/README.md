## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.12 |
| grafana | ~> 1.7 |

## Providers

| Name | Version |
|------|---------|
| grafana | ~> 1.7 |
| local | n/a |
| null | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| enable | true to enable the module | `bool` | `false` | no |
| grafana\_configuration | Configuration for creating Grafana dashboards and alerts | <pre>object({<br>    name          = string<br>    environment   = string<br>    data_source   = string<br>    notifications = list(string)<br>    lambdas       = list(string)<br>    folder        = string<br>  })</pre> | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| output | Grafana slug and dashboard\_id |

