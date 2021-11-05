from grafanalib.core import Alert, AlertCondition, Dashboard, Graph, Target
from grafanalib.cloudwatch import CloudwatchMetricsTarget
from lib.lambdas import (
    dispatcher,
    lambda_generate_duration_graph,
    lambda_generate_invocations_graph,
    lambda_generate_memory_utilization_percentage_graph,
    lambda_generate_memory_utilization_graph,
    lambda_generate_logs_panel,
    lambda_cron_dashboard,
    lambda_events_dashboard,
    lambda_cognito_dashboard,
    lambda_logs_dashboard,
    create_lambda_sqs_dlq_graph,
    create_lambda_sqs_graph,
    lambda_sqs_dashboard,
    lambda_sns_sqs_dashboard,
)


class TestDispatcher:
    def test_should_throw_exception_when_dispatcher_called_with_wrong_arguments(self):
        dispatcher.when.called_with(service="foo", trigger="bar").should.throw(
            Exception, r"dispatcher recieved a non l"
        )

    def test_should_call_trigger_handlers(self):
        expected_triggers = [
            "cognito-idp",
            "cloudwatch-event-schedule",
            "cloudwatch-event-trigger",
            "cloudwatch-logs",
            "sns",
            "sqs",
            "null",
        ]
        lambda_name = "lambda-1"
        environment = "alpha"
        topics = ["topic-1", "topic-2"]
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "influxdb_data_source": "influxdb",
            "cloudwatch_data_source": "cloudwatch",
            "lambda_insights_namespace": "insights",
            "notifications": [],
            "topics": topics,
            "fifo": False,
        }

        for trigger in expected_triggers:
            dash = dispatcher(service="lambda", trigger=trigger, **call_args)

            dash.should.be.a(Dashboard)

class TestGraphs:
    def test_should_generate_lambda_duration_graph(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace="insights"
        expected_targets = [
            CloudwatchMetricsTarget(
                alias="Min",
                namespace="AWS/Lambda",
                statistics=["Minimum"],
                metricName="Duration",
                dimensions={"FunctionName": lambda_name},
                refId="A",
            ),
            CloudwatchMetricsTarget(
                alias="Avg",
                namespace="AWS/Lambda",
                statistics=["Average"],
                metricName="Duration",
                dimensions={"FunctionName": lambda_name},
                refId="B",
            ),
            CloudwatchMetricsTarget(
                alias="Max",
                namespace="AWS/Lambda",
                statistics=["Maximum"],
                metricName="Duration",
                dimensions={"FunctionName": lambda_name},
                refId="C",
            ),
        ]
        generated_lambda_graph = lambda_generate_duration_graph(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
            lambda_insights_namespace=lambda_insights_namespace,
            notifications=[],
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "Lambda Invocation Duration"
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("alert").with_value.equal(None)
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(3)
        generated_lambda_graph.targets.should.equal(expected_targets)

    def test_should_generate_lambda_generate_invocations_graph(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace="insights"
        expected_targets = [
            CloudwatchMetricsTarget(
                alias="Invocations",
                namespace="AWS/Lambda",
                statistics=["Sum"],
                metricName="Invocations",
                dimensions={"FunctionName": lambda_name},
                refId="B",
            ),
            CloudwatchMetricsTarget(
                alias="Errors",
                namespace="AWS/Lambda",
                statistics=["Sum"],
                metricName="Errors",
                dimensions={"FunctionName": lambda_name},
                refId="A",
            ),
        ]
        generated_lambda_graph = lambda_generate_invocations_graph(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
            lambda_insights_namespace=lambda_insights_namespace,
            notifications=[],
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "Lambda Invocations and Errors"
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("alert").with_value.equal(None)
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(2)
        generated_lambda_graph.targets.should.equal(expected_targets)

    # def test_should_generate_lambda_generate_invocations_graph_with_alert_notifications(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "cloudwatch"
    #     lambda_insights_namespace="insights"
    #     notifications = ["lorem", "ipsum"]

    #     expected_alert_query = CloudwatchMetricsTarget(
    #         alias="Errors - Sum",
    #         namespace="AWS/Lambda",
    #         period="1m",
    #         statistics=["Sum"],
    #         metricName="Errors",
    #         dimensions={"FunctionName": lambda_name},
    #         refId="A",
    #     )

    #     generated_lambda_graph = lambda_generate_invocations_graph(
    #         name=lambda_name,
    #         cloudwatch_data_source=cloudwatch_data_source,
    #         lambda_insights_namespace=lambda_insights_namespace,
    #         notifications=notifications,
    #     )
    #     generated_lambda_graph.should.have.property("alert").be.a(Alert)
    #     generated_lambda_graph.alert.executionErrorState.should.eql("alerting")
    #     generated_lambda_graph.alert.noDataState.should.eql("no_data")
    #     generated_lambda_graph.alert.alertConditions.should.have.length_of(1)
    #     generated_lambda_graph.alert.alertConditions[0].should.be.a(AlertCondition)
    #     generated_lambda_graph.alert.alertConditions[0].target.should.eql(
    #         Target(refId="A")
    #     )
    #     generated_lambda_graph.targets.should.contain(expected_alert_query)

    # def test_should_generate_lambda_basic_dashboards(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "influxdb"
    #     influxdb_data_source = "influxdb"
    #     environment = "alpha"
    #     call_args = {
    #         "name": lambda_name,
    #         "environment": environment,
    #         "cloudwatch_data_source": cloudwatch_data_source,
    #         "influxdb_data_source": influxdb_data_source,
    #         "notifications": [],
    #     }

    #     test_matrix = {
    #         lambda_cron_dashboard: "cron",
    #         lambda_cognito_dashboard: "cognito",
    #         lambda_events_dashboard: "cloudwatch events",
    #         lambda_logs_dashboard: "cloudwatch logs",
    #     }

    #     for dahboard_generator, expected_dashboard_tag in test_matrix.items():
    #         generated_dashboard = dahboard_generator(**call_args)
    #         generated_dashboard.should.be.a(Dashboard)
    #         generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
    #         generated_dashboard.tags.sort().should.eql(
    #             ["lambda", environment, expected_dashboard_tag].sort()
    #         )

    # def test_should_create_lambda_sqs_dlq_graph(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "influxdb"
    #     notifications = ["lorem"]

    #     expected_alert_query = CloudwatchMetricsTarget(
    #         alias="Approximate number of messages available",
    #         namespace="AWS/SQS",
    #         period="1m",
    #         statistics=["Maximum"],
    #         metricName="ApproximateNumberOfMessagesVisible",
    #         dimensions={"QueueName": lambda_name},
    #         refId="A",
    #     )
    #     generated_lambda_graph = create_lambda_sqs_dlq_graph(
    #         name=lambda_name,
    #         cloudwatch_data_source=cloudwatch_data_source,
    #         notifications=notifications,
    #         fifo=False,
    #     )
    #     generated_lambda_graph.should.be.a(Graph)
    #     generated_lambda_graph.should.have.property("title").with_value.equal(
    #         "SQS Dead Letter Queue: {}".format(lambda_name)
    #     )
    #     generated_lambda_graph.should.have.property("dataSource").with_value.equal(
    #         cloudwatch_data_source
    #     )
    #     generated_lambda_graph.should.have.property("targets")
    #     generated_lambda_graph.targets.should.have.length_of(1)
    #     generated_lambda_graph.targets[0].should.eql(expected_alert_query)
    #     generated_lambda_graph.should.have.property("alert").be.a(Alert)
    #     generated_lambda_graph.alert.executionErrorState.should.eql("alerting")
    #     generated_lambda_graph.alert.noDataState.should.eql("no_data")

    # def test_should_create_lambda_sqs_dlq_fifo_graph(self):
    #     lambda_name = "lambda-1"
    #     sqs_dlq_name = lambda_name + "-dlq"
    #     cloudwatch_data_source = "influxdb"
    #     notifications = ["lorem"]

    #     expected_alert_query = CloudwatchMetricsTarget(
    #         alias="Approximate number of messages available",
    #         namespace="AWS/SQS",
    #         period="1m",
    #         statistics=["Maximum"],
    #         metricName="ApproximateNumberOfMessagesVisible",
    #         dimensions={"QueueName": sqs_dlq_name + ".fifo"},
    #         refId="A",
    #     )
    #     generated_lambda_graph = create_lambda_sqs_dlq_graph(
    #         name=sqs_dlq_name,
    #         cloudwatch_data_source=cloudwatch_data_source,
    #         notifications=notifications,
    #         fifo=True,
    #     )
    #     generated_lambda_graph.should.be.a(Graph)
    #     generated_lambda_graph.should.have.property("title").with_value.equal(
    #         "SQS Dead Letter Queue: {}.fifo".format(sqs_dlq_name)
    #     )
    #     generated_lambda_graph.should.have.property("dataSource").with_value.equal(
    #         cloudwatch_data_source
    #     )
    #     generated_lambda_graph.should.have.property("targets")
    #     generated_lambda_graph.targets.should.have.length_of(1)
    #     generated_lambda_graph.targets[0].should.eql(expected_alert_query)
    #     generated_lambda_graph.should.have.property("alert").be.a(Alert)
    #     generated_lambda_graph.alert.executionErrorState.should.eql("alerting")
    #     generated_lambda_graph.alert.noDataState.should.eql("no_data")

    # def test_should_create_lambda_sqs_graph(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "cloudwatch"

    #     expected_query = CloudwatchMetricsTarget(
    #         alias="Number of messages sent to the queue",
    #         namespace="AWS/SQS",
    #         period="1m",
    #         statistics=["Sum"],
    #         metricName="NumberOfMessagesSent",
    #         dimensions={"QueueName": lambda_name},
    #         refId="A",
    #     )
    #     generated_lambda_graph = create_lambda_sqs_graph(
    #         name=lambda_name, cloudwatch_data_source=cloudwatch_data_source, fifo=False
    #     )
    #     generated_lambda_graph.should.be.a(Graph)
    #     generated_lambda_graph.should.have.property("title").with_value.equal(
    #         "SQS: {}".format(lambda_name)
    #     )
    #     generated_lambda_graph.should.have.property("dataSource").with_value.equal(
    #         cloudwatch_data_source
    #     )
    #     generated_lambda_graph.should.have.property("targets")
    #     generated_lambda_graph.targets.should.have.length_of(1)
    #     generated_lambda_graph.targets[0].should.eql(expected_query)

    # def test_should_create_lambda_sqs_fifo_graph(self):
    #     lambda_name = "lambda-1"
    #     sqs_name = lambda_name + ".fifo"
    #     cloudwatch_data_source = "cloudwatch"

    #     expected_query = CloudwatchMetricsTarget(
    #         alias="Number of messages sent to the queue",
    #         namespace="AWS/SQS",
    #         period="1m",
    #         statistics=["Sum"],
    #         metricName="NumberOfMessagesSent",
    #         dimensions={"QueueName": sqs_name},
    #         refId="A",
    #     )
    #     generated_lambda_graph = create_lambda_sqs_graph(
    #         name=lambda_name, cloudwatch_data_source=cloudwatch_data_source, fifo=True
    #     )
    #     generated_lambda_graph.should.be.a(Graph)
    #     generated_lambda_graph.should.have.property("title").with_value.equal(
    #         "SQS: {}".format(sqs_name)
    #     )
    #     generated_lambda_graph.should.have.property("dataSource").with_value.equal(
    #         cloudwatch_data_source
    #     )
    #     generated_lambda_graph.should.have.property("targets")
    #     generated_lambda_graph.targets.should.have.length_of(1)
    #     generated_lambda_graph.targets[0].should.eql(expected_query)

    # def test_should_generate_lambda_sqs_dashboard(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "cloudwatch"
    #     influxdb_data_source = "influxdb"
    #     environment = "alpha"
    #     call_args = {
    #         "name": lambda_name,
    #         "environment": environment,
    #         "cloudwatch_data_source": cloudwatch_data_source,
    #         "influxdb_data_source": influxdb_data_source,
    #         "notifications": [],
    #         "fifo": False,
    #     }

    #     generated_dashboard = lambda_sqs_dashboard(**call_args)
    #     generated_dashboard.should.be.a(Dashboard)
    #     generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
    #     generated_dashboard.tags.sort().should.eql(
    #         ["lambda", environment, "sqs"].sort()
    #     )
    #     generated_dashboard.rows.should.be.length_of(3)

    # def test_should_generate_lambda_sqs_fifo_dashboard(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "cloudwatch"
    #     influxdb_data_source = "influxdb"
    #     environment = "alpha"
    #     call_args = {
    #         "name": lambda_name,
    #         "environment": environment,
    #         "cloudwatch_data_source": cloudwatch_data_source,
    #         "influxdb_data_source": influxdb_data_source,
    #         "notifications": [],
    #         "fifo": True,
    #     }

    #     generated_dashboard = lambda_sqs_dashboard(**call_args)
    #     generated_dashboard.should.be.a(Dashboard)
    #     generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
    #     generated_dashboard.tags.sort().should.eql(
    #         ["lambda", environment, "sqs", "fifo"].sort()
    #     )
    #     generated_dashboard.rows.should.be.length_of(3)

    # def test_should_generate_lambda_sns_sqs_dashboard(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "cloudwatch"
    #     influxdb_data_source = "influxdb"
    #     environment = "alpha"
    #     topics = ["topic-1", "topic-2"]
    #     call_args = {
    #         "name": lambda_name,
    #         "environment": environment,
    #         "cloudwatch_data_source": cloudwatch_data_source,
    #         "influxdb_data_source": influxdb_data_source,
    #         "notifications": [],
    #         "topics": topics,
    #         "fifo": False,
    #     }

    #     generated_dashboard = lambda_sns_sqs_dashboard(**call_args)
    #     generated_dashboard.should.be.a(Dashboard)
    #     generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
    #     generated_dashboard.tags.sort().should.eql(
    #         ["lambda", environment, "sqs", "sns"].sort()
    #     )
    #     generated_dashboard.rows.should.be.length_of(4)
    #     generated_dashboard.rows[0].panels.should.be.length_of(len(topics))

    # def test_should_generate_lambda_sns_sqs_fifo_dashboard(self):
    #     lambda_name = "lambda-1"
    #     cloudwatch_data_source = "cloudwatch"
    #     influxdb_data_source = "influxdb"
    #     environment = "alpha"
    #     topics = ["topic-1", "topic-2"]
    #     call_args = {
    #         "name": lambda_name,
    #         "environment": environment,
    #         "cloudwatch_data_source": cloudwatch_data_source,
    #         "influxdb_data_source": influxdb_data_source,
    #         "notifications": [],
    #         "topics": topics,
    #         "fifo": True,
    #     }

    #     generated_dashboard = lambda_sns_sqs_dashboard(**call_args)
    #     generated_dashboard.should.be.a(Dashboard)
    #     generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
    #     generated_dashboard.tags.sort().should.eql(
    #         ["lambda", environment, "sqs", "sns", "fifo"].sort()
    #     )
    #     generated_dashboard.rows.should.be.length_of(4)
    #     generated_dashboard.rows[0].panels.should.be.length_of(len(topics))
