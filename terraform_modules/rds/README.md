## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.13 |

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
| grafana\_configuration | Configuration for creating Grafana dashboards and alerts | <pre>object({<br>    name                   = string<br>    environment            = string<br>    influxdb_data_source   = string<br>    cloudwatch_data_source = string<br>    folder                 = string<br>    engine                 = string<br>    notifications          = list(string)<br>  })</pre> | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| output | Grafana slug and dashboard\_id |
