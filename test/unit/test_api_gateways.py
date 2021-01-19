from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    Target,
    Annotations,
    Templating,
)
from grafanalib.cloudwatch import CloudwatchMetricsTarget

from lib.api_gateways import (
    generate_api_gateway_requests_5xx_graph,
    generate_api_gateway_requests_4xx_graph,
    generate_api_gateways_dashboard,
)

import re


class TestAPIGatewayDashboards:
    def test_should_generate_proper_requests_5xx_graph(self):
        apig_name = "apig-1"
        cloudwatch_data_source = "prod"
        influxdb_data_source = "influxdb"
        notifications = []

        targets = [
            CloudwatchMetricsTarget(
                alias="5xx",
                namespace="AWS/ApiGateway",
                period="1m",
                statistics=["Sum"],
                metricName="5XXError",
                dimensions={"ApiName": apig_name},
                refId="A",
            ),
            CloudwatchMetricsTarget(
                alias="requests",
                namespace="AWS/ApiGateway",
                dimensions={"ApiName": apig_name},
                period="1m",
                statistics=["Sum"],
                metricName="Count",
                refId="B",
            ),
        ]

        generated_graph = generate_api_gateway_requests_5xx_graph(
            name=apig_name,
            cloudwatch_data_source=cloudwatch_data_source,
            influxdb_data_source=influxdb_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"API Gateway Requests and 5XX errors")
        generated_graph.dataSource.should.eql(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(len(targets))
        generated_graph.alert.should.eql(None)

    def test_should_generate_proper_requests_5xx_graph_with_notifications(self):
        apig_name = "apig-1"
        cloudwatch_data_source = "prod"
        influxdb_data_source = "influxdb"
        notifications = ["foo-1", "foo-2"]

        targets = [
            CloudwatchMetricsTarget(
                alias="5xx",
                namespace="AWS/ApiGateway",
                period="1m",
                statistics=["Sum"],
                metricName="5XXError",
                dimensions={"ApiName": apig_name},
                refId="A",
            ),
            CloudwatchMetricsTarget(
                alias="requests",
                namespace="AWS/ApiGateway",
                dimensions={"ApiName": apig_name},
                period="1m",
                statistics=["Sum"],
                metricName="Count",
                refId="B",
            ),
        ]

        generated_graph = generate_api_gateway_requests_5xx_graph(
            name=apig_name,
            cloudwatch_data_source=cloudwatch_data_source,
            influxdb_data_source=influxdb_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"API Gateway Requests and 5XX errors")
        generated_graph.dataSource.should.eql(cloudwatch_data_source)
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.alertConditions.should.have.length_of(1)
        generated_graph.alert.alertConditions[0].target.should.equal(Target(refId="A"))
        generated_graph.targets[0].should.eql(targets[0])

    def test_should_generate_proper_requests_4xx_graph(self):
        apig_name = "apig-1"
        cloudwatch_data_source = "prod"
        influxdb_data_source = "influxdb"

        targets = [
            CloudwatchMetricsTarget(
                alias="4xx",
                namespace="AWS/ApiGateway",
                period="1m",
                statistics=["Sum"],
                metricName="4XXError",
                dimensions={"ApiName": apig_name},
                refId="A",
            ),
            CloudwatchMetricsTarget(
                alias="requests",
                namespace="AWS/ApiGateway",
                dimensions={"ApiName": apig_name},
                period="1m",
                statistics=["Sum"],
                metricName="Count",
                refId="B",
            ),
        ]

        generated_graph = generate_api_gateway_requests_4xx_graph(
            name=apig_name,
            cloudwatch_data_source=cloudwatch_data_source,
            influxdb_data_source=influxdb_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"API Gateway Requests and 4XX errors")
        generated_graph.dataSource.should.eql(cloudwatch_data_source)
        generated_graph.alert.should.equal(None)
        generated_graph.targets.should.have.length_of(2)
        generated_graph.targets.should.equal(targets)

    def test_should_generate_proper_dashboard(self):
        apig_name = "apig-1"
        cloudwatch_data_source = "prod"
        influxdb_data_source = "influxdb"
        environment = "prod"
        notifications = ["foo-1", "foo-2"]
        lambdas = []

        generated_dashboard = generate_api_gateways_dashboard(
            name=apig_name,
            cloudwatch_data_source=cloudwatch_data_source,
            influxdb_data_source=influxdb_data_source,
            notifications=notifications,
            environment=environment,
            lambdas=lambdas,
        )

        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.match(r"API Gateway:")
        generated_dashboard.annotations.should.be.a(Annotations)
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.tags.should.have.length_of(2)
        generated_dashboard.rows.should.have.length_of(2)

    def test_should_generate_proper_dashboard_with_lambdas(self):
        apig_name = "apig-1"
        cloudwatch_data_source = "prod"
        influxdb_data_source = "influxdb"
        environment = "prod"
        notifications = ["foo-1", "foo-2"]
        lambdas = ["lambda-1", "lambda-2"]

        generated_dashboard = generate_api_gateways_dashboard(
            name=apig_name,
            cloudwatch_data_source=cloudwatch_data_source,
            influxdb_data_source=influxdb_data_source,
            notifications=notifications,
            environment=environment,
            lambdas=lambdas,
        )

        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.match(r"API Gateway:")
        generated_dashboard.annotations.should.be.a(Annotations)
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.tags.should.have.length_of(3)
        generated_dashboard.rows.should.have.length_of(3)
