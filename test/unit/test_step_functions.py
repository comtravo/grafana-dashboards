from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    Target,
    Annotations,
    Templating,
    OP_OR,
)
from grafanalib.influxdb import InfluxDBTarget

from lib.step_functions import generate_sfn_graph, generate_sfn_dashboard

import re


class TestStepFunctionDashboards:
    def test_should_generate_sfn_graph_without_notifications(self):
        sfn_name = "sfn-1"
        data_source = "prod"
        notifications = []

        generated_graph = generate_sfn_graph(
            name=sfn_name, data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Step function execution metrics")
        generated_graph.dataSource.should.equal(data_source)
        generated_graph.targets.should.have.length_of(9)
        generated_graph.alert.should.be(None)

    def test_should_generate_sfn_graph_with_notifications(self):
        sfn_name = "sfn-1"
        data_source = "prod"
        notifications = ["lorem", "ipsum"]

        expected_targets = [
            InfluxDBTarget(
                query='SELECT min("execution_time_minimum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
            ),
            InfluxDBTarget(
                query='SELECT mean("execution_time_average") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
            ),
            InfluxDBTarget(
                query='SELECT max("execution_time_maximum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
            ),
            InfluxDBTarget(
                query='SELECT max("executions_started_sum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
            ),
            InfluxDBTarget(
                query='SELECT max("executions_succeeded_sum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
            ),
            InfluxDBTarget(
                query='SELECT max("executions_aborted_sum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
                refId="A",
            ),
            InfluxDBTarget(
                query='SELECT max("executions_failed_sum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
                refId="B",
            ),
            InfluxDBTarget(
                query='SELECT max("execution_throttled_sum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
                refId="C",
            ),
            InfluxDBTarget(
                query='SELECT max("execution_timed_out_sum") FROM "autogen"."cloudwatch_aws_states" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                    sfn_name
                ),
                refId="D",
            ),
        ]

        generated_graph = generate_sfn_graph(
            name=sfn_name, data_source=data_source, notifications=notifications
        )
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.eql("2m")
        generated_graph.alert.gracePeriod.should.eql("2m")
        generated_graph.alert.notifications.should.eql(notifications)

        generated_graph.alert.alertConditions.should.have.length_of(4)
        generated_graph.alert.alertConditions[0].target.should.equal(Target(refId="A"))
        generated_graph.alert.alertConditions[0].operator.should.equal(OP_OR)
        generated_graph.alert.alertConditions[1].target.should.equal(Target(refId="B"))
        generated_graph.alert.alertConditions[1].operator.should.equal(OP_OR)
        generated_graph.alert.alertConditions[2].target.should.equal(Target(refId="C"))
        generated_graph.alert.alertConditions[2].operator.should.equal(OP_OR)
        generated_graph.alert.alertConditions[3].target.should.equal(Target(refId="D"))
        generated_graph.alert.alertConditions[3].operator.should.equal(OP_OR)

    def test_should_generate_proper_dashboard(self):
        name = "sfn-1"
        data_source = "prod"
        environment = "prod"
        notifications = ["foo-1", "foo-2"]
        lambdas = []

        generated_dashboard = generate_sfn_dashboard(
            name=name,
            data_source=data_source,
            notifications=notifications,
            environment=environment,
            lambdas=lambdas,
        )

        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.match(r"Step Function:")
        generated_dashboard.annotations.should.be.a(Annotations)
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.tags.should.have.length_of(2)
        generated_dashboard.rows.should.have.length_of(1)

    def test_should_generate_proper_dashboard_with_dashboards(self):
        name = "sfn-1"
        data_source = "prod"
        environment = "prod"
        notifications = ["foo-1", "foo-2"]
        lambdas = ["lambda-1", "lambda-2"]

        generated_dashboard = generate_sfn_dashboard(
            name=name,
            data_source=data_source,
            notifications=notifications,
            environment=environment,
            lambdas=lambdas,
        )

        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.match(r"Step Function:")
        generated_dashboard.annotations.should.be.a(Annotations)
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.tags.should.have.length_of(3)
        generated_dashboard.rows.should.have.length_of(2)
