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
from grafanalib.cloudwatch import CloudwatchMetricsTarget

from lib.step_functions import (
    generate_sfn_execution_metrics_graph,
    generate_sfn_dashboard,
)

import re


class TestStepFunctionDashboards:
    def test_should_generate_sfn_execution_metrics_graph_without_notifications(self):
        sfn_name = "arn:aws:states:eu-west-1:1234567890:stateMachine:sfn-1"
        cloudwatch_data_source = "prod"
        notifications = []

        generated_graph = generate_sfn_execution_metrics_graph(
            name=sfn_name,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Step function execution metrics")
        generated_graph.dataSource.should.equal(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(6)
        generated_graph.alert.should.be(None)

    def test_should_generate_sfn_execution_metrics_graph_with_notifications(self):
        sfn_name = "arn:aws:states:eu-west-1:1234567890:stateMachine:sfn-1"
        cloudwatch_data_source = "prod"
        notifications = ["lorem", "ipsum"]

        expected_targets = [
            CloudwatchMetricsTarget(
                alias="Executions - Started",
                namespace="AWS/States",
                metricName="ExecutionsStarted",
                statistics=["Sum"],
                dimensions={"StateMachineArn": sfn_name},
                refId="E",
            ),
            CloudwatchMetricsTarget(
                alias="Executions - Succeeded",
                namespace="AWS/States",
                metricName="ExecutionsSucceeded",
                statistics=["Sum"],
                dimensions={"StateMachineArn": sfn_name},
                refId="F",
            ),
            CloudwatchMetricsTarget(
                alias="Executions - Aborted",
                namespace="AWS/States",
                metricName="ExecutionsAborted",
                statistics=["Sum"],
                dimensions={"StateMachineArn": sfn_name},
                refId="A",
            ),
            CloudwatchMetricsTarget(
                alias="Executions - Failed",
                namespace="AWS/States",
                metricName="ExecutionsFailed",
                statistics=["Sum"],
                dimensions={"StateMachineArn": sfn_name},
                refId="B",
            ),
            CloudwatchMetricsTarget(
                alias="Executions - Throttled",
                namespace="AWS/States",
                metricName="ExecutionsThrottled",
                statistics=["Sum"],
                dimensions={"StateMachineArn": sfn_name},
                refId="C",
            ),
            CloudwatchMetricsTarget(
                alias="Executions - Timeout",
                namespace="AWS/States",
                metricName="ExecutionsTimedOut",
                statistics=["Sum"],
                dimensions={"StateMachineArn": sfn_name},
                refId="D",
            ),
        ]

        generated_graph = generate_sfn_execution_metrics_graph(
            name=sfn_name,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.eql("2m")
        generated_graph.alert.gracePeriod.should.eql("2m")
        generated_graph.alert.notifications.should.eql(notifications)

        generated_graph.targets.should.equal(expected_targets)

        generated_graph.alert.alertConditions.should.have.length_of(4)
        generated_graph.alert.alertConditions[0].target.should.equal(Target(refId="A"))
        generated_graph.alert.alertConditions[0].operator.should.equal(OP_OR)
        generated_graph.alert.alertConditions[1].target.should.equal(Target(refId="B"))
        generated_graph.alert.alertConditions[1].operator.should.equal(OP_OR)
        generated_graph.alert.alertConditions[2].target.should.equal(Target(refId="C"))
        generated_graph.alert.alertConditions[2].operator.should.equal(OP_OR)
        generated_graph.alert.alertConditions[3].target.should.equal(Target(refId="D"))
        generated_graph.alert.alertConditions[3].operator.should.equal(OP_OR)

    # def test_should_generate_proper_dashboard(self):
    #     name = "arn:aws:states:eu-west-1:1234567890:stateMachine:sfn-1"
    #     cloudwatch_data_source = "prod"
    #     influxdb_data_source = "prod"
    #     environment = "prod"
    #     notifications = ["foo-1", "foo-2"]
    #     lambdas = []

    #     generated_dashboard = generate_sfn_dashboard(
    #         name=name,
    #         cloudwatch_data_source=cloudwatch_data_source,
    #         influxdb_data_source=influxdb_data_source,
    #         notifications=notifications,
    #         environment=environment,
    #         lambdas=lambdas,
    #     )

    #     generated_dashboard.should.be.a(Dashboard)
    #     generated_dashboard.title.should.match(r"Step Function:")
    #     generated_dashboard.annotations.should.be.a(Annotations)
    #     generated_dashboard.templating.should.be.a(Templating)
    #     generated_dashboard.tags.should.have.length_of(2)
    #     generated_dashboard.rows.should.have.length_of(1)

    # def test_should_throw_error_when_sfn_arn_not_specified(self):
    #     name = "sfn-1"
    #     cloudwatch_data_source = "prod"
    #     influxdb_data_source = "prod"
    #     environment = "prod"
    #     notifications = ["foo-1", "foo-2"]
    #     lambdas = ["lambda-1", "lambda-2"]

    #     generate_sfn_dashboard.when.called_with(
    #         name=name,
    #         cloudwatch_data_source=cloudwatch_data_source,
    #         influxdb_data_source=influxdb_data_source,
    #         notifications=notifications,
    #         environment=environment,
    #         lambdas=lambdas,
    #     ).should.throw(Exception, r"Statemachine ARN should be provided")

    # def test_should_generate_proper_dashboard_with_arn(self):
    #     name = "arn:aws:states:eu-west-1:1234567890:stateMachine:sfn-1"
    #     cloudwatch_data_source = "prod"
    #     influxdb_data_source = "prod"
    #     environment = "prod"
    #     notifications = ["foo-1", "foo-2"]
    #     lambdas = ["lambda-1", "lambda-2"]

    #     generated_dashboard = generate_sfn_dashboard(
    #         name=name,
    #         cloudwatch_data_source=cloudwatch_data_source,
    #         influxdb_data_source=influxdb_data_source,
    #         notifications=notifications,
    #         environment=environment,
    #         lambdas=lambdas,
    #     )
    #     generated_dashboard.title.should.match(r"Step Function: sfn-1")
