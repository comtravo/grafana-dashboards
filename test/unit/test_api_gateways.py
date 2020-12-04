from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    Target,
    Annotations,
    Templating,
)
from grafanalib.influxdb import InfluxDBTarget

from lib.api_gateways import (
    generate_api_gateway_requests_5xx_graph,
    generate_api_gateway_requests_4xx_graph,
    generate_api_gateways_dashboard,
)

import re


class TestAPIGatewayDashboards:
    def test_should_generate_proper_requests_5xx_graph(self):
        apig_name = "apig-1"
        data_source = "prod"
        notifications = []

        expected_targets = [
            InfluxDBTarget(
                alias="5xx",
                query='SELECT sum("5xx_error_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
            ),
            InfluxDBTarget(
                alias="requests",
                query='SELECT sum("count_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
            ),
        ]

        generated_graph = generate_api_gateway_requests_5xx_graph(
            name=apig_name, data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"API Gateway Requests and 5XX errors")
        generated_graph.dataSource.should.eql(data_source)
        generated_graph.targets.should.have.length_of(len(expected_targets))
        generated_graph.alert.should.eql(None)

    def test_should_generate_proper_requests_5xx_graph_with_notifications(self):
        apig_name = "apig-1"
        data_source = "prod"
        notifications = ["foo-1", "foo-2"]

        expected_alert_query = InfluxDBTarget(
            alias="5xx",
            query='SELECT sum("5xx_error_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                apig_name
            ),
            rawQuery=True,
            refId="A",
        )

        generated_graph = generate_api_gateway_requests_5xx_graph(
            name=apig_name, data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"API Gateway Requests and 5XX errors")
        generated_graph.dataSource.should.eql(data_source)
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.alertConditions.should.have.length_of(1)
        generated_graph.alert.alertConditions[0].target.should.equal(Target(refId="A"))
        generated_graph.targets[0].should.eql(expected_alert_query)

    def test_should_generate_proper_requests_4xx_graph(self):
        apig_name = "apig-1"
        data_source = "prod"
        notifications = []

        expected_targets = [
            InfluxDBTarget(
                alias="4xx",
                query='SELECT sum("4xx_error_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
            ),
            InfluxDBTarget(
                alias="requests",
                query='SELECT sum("count_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
            ),
            InfluxDBTarget(
                alias="requests",
                query='SELECT sum("4xx_error_sum")/sum("count_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
            ),
        ]

        generated_graph = generate_api_gateway_requests_4xx_graph(
            name=apig_name, data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"API Gateway Requests and 4XX errors")
        generated_graph.dataSource.should.eql(data_source)
        generated_graph.targets.should.have.length_of(len(expected_targets))
        generated_graph.alert.should.eql(None)

    def test_should_generate_proper_requests_4xx_graph_with_notifications(self):
        apig_name = "apig-1"
        data_source = "prod"
        notifications = ["foo-1", "foo-2"]

        expected_alert_query = targets = [
            InfluxDBTarget(
                alias="4xx",
                query='SELECT sum("4xx_error_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
                rawQuery=True,
                refId="B",
            ),
            InfluxDBTarget(
                alias="requests",
                query='SELECT sum("count_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
                rawQuery=True,
                refId="C",
            ),
            InfluxDBTarget(
                alias="alert_query",
                query='SELECT sum("4xx_error_sum")/sum("count_sum") FROM "autogen"."cloudwatch_aws_api_gateway" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                    apig_name
                ),
                rawQuery=True,
                refId="A",
            ),
        ]

        generated_graph = generate_api_gateway_requests_4xx_graph(
            name=apig_name, data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"API Gateway Requests and 4XX errors")
        generated_graph.dataSource.should.eql(data_source)
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.alertConditions.should.have.length_of(2)
        generated_graph.alert.alertConditions[0].target.should.equal(Target(refId="C"))
        generated_graph.alert.alertConditions[1].target.should.equal(Target(refId="A"))
        generated_graph.targets.should.eql(expected_alert_query)

    def test_should_generate_proper_dashboard(self):
        apig_name = "apig-1"
        data_source = "prod"
        environment = "prod"
        notifications = ["foo-1", "foo-2"]
        lambdas = []

        generated_dashboard = generate_api_gateways_dashboard(
            name=apig_name,
            data_source=data_source,
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
        data_source = "prod"
        environment = "prod"
        notifications = ["foo-1", "foo-2"]
        lambdas = ["lambda-1", "lambda-2"]

        generated_dashboard = generate_api_gateways_dashboard(
            name=apig_name,
            data_source=data_source,
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
