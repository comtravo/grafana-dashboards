# Grafana Dashboards 📈 📟

- [Grafana Dashboards 📈 📟](#grafana-dashboards--)
  - [What are we trying to solve](#what-are-we-trying-to-solve)
    - [Problems](#problems)
  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Development](#development)
  - [Examples](#examples)
  - [TODO](#todo)

## What are we trying to solve

You might have heard about Infrastructure as Code (IaC) to define your infrastructure. It enables GitOps which helps in improving code deployment velocity and testing of Infrastructure. It is also scalable and makes rolling back infrastructure changes easier upon failures. Dashboard as code is a similar concept.

With Grafana, one can not only define dashboards but also alerts. When one visits a dashboard, it is expected that the dashboard gives a complete picture of how a particular system in your cloud infrastructure is functioning. Grafana Labs [talks in detail](https://grafana.com/docs/grafana/latest/best-practices/common-observability-strategies/) on how to create such dashboards. Grafana provides a way to [define these dashboards and alerts](https://grafana.com/docs/grafana/latest/administration/provisioning/). However, they come with their own disadvantages.

### Problems

- No human could possibliy create them by hand and maintain them. Scalability is an issue. [Read more about Grafana JSON model](https://grafana.com/docs/grafana/latest/dashboards/json-model/)
- Cannot apply CI CD practices
- Code re-usability is non-existent
- Cannot apply changes across all dashboards and alerts
- Automated dashboard and alert provisioning and de-provisioning using IaC.
  - Given the serverless trend today, your cloud infrastructure can have various functions that are triggered by ways. In such cases, it is difficult to create individual dashboards and maintain them. They get renamed, moved and  deleted

## Introduction

This project (very much a WIP) generates dynamic Grafana canned dashboards and alerts for various services that are running on AWS. This project assumes that you are running [InfluxDB](https://www.influxdata.com/products/influxdb/) as the time series database and using [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) for scraping cloudwatch metrics. This project also contains [Terraform](https://www.terraform.io/) modules in the [terraform_modules](./terraform_modules/) folder to integrate with your Terraform code. This project makes use of [Grafanalib](https://grafanalib.readthedocs.io/en/latest/index.html) to generate dashboards and alerts

## Requirements

The project uses [Grafanalib](https://grafanalib.readthedocs.io/en/latest/index.html) project to generate dynamic dashboards. So, it is expected that `python3` and `pip3` are available in the runtime environment. If you want to Terraform your dashboards, further requirements include Terraform.

## Development

The dashboards and alerts are generated in `python3`. So you would require `python3` and `pip3`. Furthermore, if you need to develop companion terraform modules, you would require `golang:1.14`. It is however recommended that you use `Docker` and the `make develop` target to start developing dashboards and terraform modules.

Useful make targets:

- `make build` builds the docker images for local development
- `make test-docker` runs tests for the previously build docker images
- `make lint` checks currently the code formatting
- `make fmt` formats your terraform, go and python code
- `make test` runs unit and integration tests
- `make generate-docs` generates the terraform docs

## Examples

The [examples](./examples) directory showcases various possibilies on using the terraform modules. They are also used as part of the integration tests in this project.

## TODO

 - [ ] Create snapshots of dasboards in the [examples](./examples) directory
 - [ ] Add ECS
 - [ ] Add MongoDB
