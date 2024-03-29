from grafanalib.cloudwatch import CloudwatchLogsInsightsTarget, CloudwatchMetricsTarget
from grafanalib.core import Alert, AlertCondition, Dashboard, Graph, Panel, Target

from lib.lambdas import (
    create_lambda_sqs_dlq_graph,
    create_lambda_sqs_graph,
    dispatcher,
    lambda_cognito_dashboard,
    lambda_cron_dashboard,
    lambda_events_dashboard,
    lambda_generate_duration_graph,
    lambda_generate_invocations_graph,
    lambda_generate_logs_panel,
    lambda_generate_memory_utilization_graph,
    lambda_generate_memory_utilization_percentage_graph,
    lambda_logs_dashboard,
    lambda_sns_sqs_dashboard,
    lambda_sqs_dashboard,
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
        lambda_insights_namespace = "insights"
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

    def test_should_generate_lambda_invocations_graph(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
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

    def test_should_generate_lambda_invocations_graph_with_alert_notifications(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        notifications = ["lorem", "ipsum"]

        expected_alert_query = CloudwatchMetricsTarget(
            alias="Errors",
            namespace="AWS/Lambda",
            statistics=["Sum"],
            metricName="Errors",
            dimensions={"FunctionName": lambda_name},
            refId="A",
        )

        generated_lambda_graph = lambda_generate_invocations_graph(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
            lambda_insights_namespace=lambda_insights_namespace,
            notifications=notifications,
        )
        generated_lambda_graph.should.have.property("alert").be.a(Alert)
        generated_lambda_graph.alert.executionErrorState.should.eql("alerting")
        generated_lambda_graph.alert.noDataState.should.eql("no_data")
        generated_lambda_graph.alert.alertConditions.should.have.length_of(1)
        generated_lambda_graph.alert.alertConditions[0].should.be.a(AlertCondition)
        generated_lambda_graph.alert.alertConditions[0].target.should.eql(
            Target(refId="A")
        )
        generated_lambda_graph.targets.should.contain(expected_alert_query)

    def test_should_generate_lambda_memory_utilization_percentage_graph(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        expected_targets = [
            CloudwatchMetricsTarget(
                alias="Min",
                namespace=lambda_insights_namespace,
                statistics=["Minimum"],
                metricName="memory_utilization",
                dimensions={"function_name": lambda_name},
                refId="B",
            ),
            CloudwatchMetricsTarget(
                alias="Avg",
                namespace=lambda_insights_namespace,
                statistics=["Average"],
                metricName="memory_utilization",
                dimensions={"function_name": lambda_name},
                refId="A",
            ),
            CloudwatchMetricsTarget(
                alias="Max",
                namespace=lambda_insights_namespace,
                statistics=["Maximum"],
                metricName="memory_utilization",
                dimensions={"function_name": lambda_name},
                refId="C",
            ),
        ]
        generated_lambda_graph = lambda_generate_memory_utilization_percentage_graph(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
            lambda_insights_namespace=lambda_insights_namespace,
            notifications=[],
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "Lambda Memory Utilization Percentage"
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("alert").with_value.equal(None)
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(3)
        generated_lambda_graph.targets.should.equal(expected_targets)

    def test_should_generate_lambda_memory_utilization_percentage_graph_with_alert_notifications(
        self,
    ):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        notifications = ["lorem", "ipsum"]

        expected_alert_query = CloudwatchMetricsTarget(
            alias="Avg",
            namespace=lambda_insights_namespace,
            statistics=["Average"],
            metricName="memory_utilization",
            dimensions={"function_name": lambda_name},
            refId="A",
        )

        generated_lambda_graph = lambda_generate_memory_utilization_percentage_graph(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
            lambda_insights_namespace=lambda_insights_namespace,
            notifications=notifications,
        )
        generated_lambda_graph.should.have.property("alert").be.a(Alert)
        generated_lambda_graph.alert.executionErrorState.should.eql("alerting")
        generated_lambda_graph.alert.noDataState.should.eql("no_data")
        generated_lambda_graph.alert.alertConditions.should.have.length_of(1)
        generated_lambda_graph.alert.alertConditions[0].should.be.a(AlertCondition)
        generated_lambda_graph.alert.alertConditions[0].target.should.eql(
            Target(refId="A")
        )
        generated_lambda_graph.targets.should.contain(expected_alert_query)

    def test_should_generate_lambda_memory_utilization_percentage_graph(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        expected_targets = [
            CloudwatchMetricsTarget(
                alias="used_memory_max",
                namespace=lambda_insights_namespace,
                statistics=["Maximum"],
                metricName="used_memory_max",
                dimensions={"function_name": lambda_name},
                refId="A",
            ),
            CloudwatchMetricsTarget(
                alias="allocated_memory",
                namespace=lambda_insights_namespace,
                statistics=["Maximum"],
                metricName="total_memory",
                dimensions={"function_name": lambda_name},
                refId="B",
            ),
        ]
        generated_lambda_graph = lambda_generate_memory_utilization_graph(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
            lambda_insights_namespace=lambda_insights_namespace,
            notifications=[],
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "Lambda Memory Utilization"
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("alert").with_value.equal(None)
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(2)
        generated_lambda_graph.targets.should.equal(expected_targets)

    def test_should_generate_generate_logs_panel(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        expected_targets = [
            CloudwatchLogsInsightsTarget(
                expression="fields @timestamp, @message | filter @message like /^(?!.*(START|END|REPORT|LOGS|EXTENSION)).*$/ | sort @timestamp desc",
                logGroupNames=["/aws/lambda/{}".format(lambda_name)],
            ),
        ]
        generated_lambda_graph = lambda_generate_logs_panel(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_lambda_graph.should.be.a(Panel)
        generated_lambda_graph.should.have.property("title").with_value.equal("Logs")
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(1)
        generated_lambda_graph.targets.should.equal(expected_targets)
        generated_lambda_graph.wrapLogMessages.should.equal(True)
        generated_lambda_graph.prettifyLogMessage.should.equal(False)
        generated_lambda_graph.enableLogDetails.should.equal(True)

    def test_should_generate_lambda_basic_dashboards(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "influxdb"
        lambda_insights_namespace = "insights"
        environment = "alpha"
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "cloudwatch_data_source": cloudwatch_data_source,
            "lambda_insights_namespace": lambda_insights_namespace,
            "notifications": [],
        }

        test_matrix = {
            lambda_cron_dashboard: "cron",
            lambda_cognito_dashboard: "cognito",
            lambda_events_dashboard: "cloudwatch events",
            lambda_logs_dashboard: "cloudwatch logs",
        }

        for dahboard_generator, expected_dashboard_tag in test_matrix.items():
            generated_dashboard = dahboard_generator(**call_args)
            generated_dashboard.should.be.a(Dashboard)
            generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
            sorted(generated_dashboard.tags).should.eql(
                sorted(["lambda", environment, expected_dashboard_tag])
            )

    def test_should_create_lambda_sqs_dlq_graph(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "influxdb"
        notifications = ["lorem"]

        expected_alert_query = CloudwatchMetricsTarget(
            alias="Approximate number of messages available",
            namespace="AWS/SQS",
            statistics=["Maximum"],
            metricName="ApproximateNumberOfMessagesVisible",
            dimensions={"QueueName": lambda_name},
            refId="A",
        )
        generated_lambda_graph = create_lambda_sqs_dlq_graph(
            name=lambda_name,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
            fifo=False,
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "SQS Dead Letter Queue: {}".format(lambda_name)
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(1)
        generated_lambda_graph.targets[0].should.eql(expected_alert_query)
        generated_lambda_graph.should.have.property("alert").be.a(Alert)
        generated_lambda_graph.alert.executionErrorState.should.eql("alerting")
        generated_lambda_graph.alert.noDataState.should.eql("no_data")

    def test_should_create_lambda_sqs_dlq_fifo_graph(self):
        lambda_name = "lambda-1"
        sqs_dlq_name = lambda_name + "-dlq"
        cloudwatch_data_source = "influxdb"
        notifications = ["lorem"]

        expected_alert_query = CloudwatchMetricsTarget(
            alias="Approximate number of messages available",
            namespace="AWS/SQS",
            statistics=["Maximum"],
            metricName="ApproximateNumberOfMessagesVisible",
            dimensions={"QueueName": sqs_dlq_name + ".fifo"},
            refId="A",
        )
        generated_lambda_graph = create_lambda_sqs_dlq_graph(
            name=sqs_dlq_name,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
            fifo=True,
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "SQS Dead Letter Queue: {}.fifo".format(sqs_dlq_name)
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(1)
        generated_lambda_graph.targets[0].should.eql(expected_alert_query)
        generated_lambda_graph.should.have.property("alert").be.a(Alert)
        generated_lambda_graph.alert.executionErrorState.should.eql("alerting")
        generated_lambda_graph.alert.noDataState.should.eql("no_data")

    def test_should_create_lambda_sqs_graph(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"

        expected_query = CloudwatchMetricsTarget(
            alias="Number of messages sent to the queue",
            namespace="AWS/SQS",
            statistics=["Sum"],
            metricName="NumberOfMessagesSent",
            dimensions={"QueueName": lambda_name},
            refId="A",
        )
        generated_lambda_graph = create_lambda_sqs_graph(
            name=lambda_name, cloudwatch_data_source=cloudwatch_data_source, fifo=False
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "SQS: {}".format(lambda_name)
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(1)
        generated_lambda_graph.targets[0].should.eql(expected_query)

    def test_should_create_lambda_sqs_fifo_graph(self):
        lambda_name = "lambda-1"
        sqs_name = lambda_name + ".fifo"
        cloudwatch_data_source = "cloudwatch"

        expected_query = CloudwatchMetricsTarget(
            alias="Number of messages sent to the queue",
            namespace="AWS/SQS",
            statistics=["Sum"],
            metricName="NumberOfMessagesSent",
            dimensions={"QueueName": sqs_name},
            refId="A",
        )
        generated_lambda_graph = create_lambda_sqs_graph(
            name=lambda_name, cloudwatch_data_source=cloudwatch_data_source, fifo=True
        )
        generated_lambda_graph.should.be.a(Graph)
        generated_lambda_graph.should.have.property("title").with_value.equal(
            "SQS: {}".format(sqs_name)
        )
        generated_lambda_graph.should.have.property("dataSource").with_value.equal(
            cloudwatch_data_source
        )
        generated_lambda_graph.should.have.property("targets")
        generated_lambda_graph.targets.should.have.length_of(1)
        generated_lambda_graph.targets[0].should.eql(expected_query)

    def test_should_generate_lambda_sqs_dashboard(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        environment = "alpha"
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "cloudwatch_data_source": cloudwatch_data_source,
            "lambda_insights_namespace": lambda_insights_namespace,
            "notifications": [],
            "fifo": False,
        }

        generated_dashboard = lambda_sqs_dashboard(**call_args)
        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
        sorted(generated_dashboard.tags).should.eql(
            sorted(["lambda", environment, "sqs"])
        )
        generated_dashboard.rows.should.be.length_of(5)
        generated_dashboard.rows[0].title.should.eql("Invocations")
        generated_dashboard.rows[0].panels.should.be.length_of(2)
        generated_dashboard.rows[1].title.should.eql("Memory Utilization")
        generated_dashboard.rows[1].panels.should.be.length_of(2)
        generated_dashboard.rows[2].title.should.eql("Logs")
        generated_dashboard.rows[2].panels.should.be.length_of(1)
        generated_dashboard.rows[3].title.should.eql("Queues")
        generated_dashboard.rows[3].panels.should.be.length_of(1)
        generated_dashboard.rows[4].title.should.eql("Dead Letter Queues")
        generated_dashboard.rows[4].panels.should.be.length_of(1)

    def test_should_generate_lambda_sqs_fifo_dashboard(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        environment = "alpha"
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "cloudwatch_data_source": cloudwatch_data_source,
            "lambda_insights_namespace": lambda_insights_namespace,
            "notifications": [],
            "fifo": True,
        }

        generated_dashboard = lambda_sqs_dashboard(**call_args)
        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
        sorted(generated_dashboard.tags).should.eql(
            sorted(["lambda", environment, "sqs", "fifo"])
        )
        generated_dashboard.rows.should.be.length_of(5)
        generated_dashboard.rows[0].title.should.eql("Invocations")
        generated_dashboard.rows[0].panels.should.be.length_of(2)
        generated_dashboard.rows[1].title.should.eql("Memory Utilization")
        generated_dashboard.rows[1].panels.should.be.length_of(2)
        generated_dashboard.rows[2].title.should.eql("Logs")
        generated_dashboard.rows[2].panels.should.be.length_of(1)
        generated_dashboard.rows[3].title.should.eql("Queues")
        generated_dashboard.rows[3].panels.should.be.length_of(1)
        generated_dashboard.rows[4].title.should.eql("Dead Letter Queues")
        generated_dashboard.rows[4].panels.should.be.length_of(1)

    def test_should_generate_lambda_sns_sqs_dashboard(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        environment = "alpha"
        topics = ["topic-1", "topic-2"]
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "cloudwatch_data_source": cloudwatch_data_source,
            "lambda_insights_namespace": lambda_insights_namespace,
            "notifications": [],
            "fifo": False,
            "topics": topics,
        }

        generated_dashboard = lambda_sns_sqs_dashboard(**call_args)
        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
        sorted(generated_dashboard.tags).should.eql(
            sorted(["lambda", environment, "sqs", "sns"])
        )
        generated_dashboard.rows.should.be.length_of(6)
        generated_dashboard.rows[0].panels.should.be.length_of(len(topics))
        generated_dashboard.rows[0].title.should.eql("SNS Topics")

        generated_dashboard.rows[1].title.should.eql("Invocations")
        generated_dashboard.rows[1].panels.should.be.length_of(2)

        generated_dashboard.rows[2].title.should.eql("Memory Utilization")
        generated_dashboard.rows[2].panels.should.be.length_of(2)

        generated_dashboard.rows[3].title.should.eql("Logs")
        generated_dashboard.rows[3].panels.should.be.length_of(1)

        generated_dashboard.rows[4].title.should.eql("Queues")
        generated_dashboard.rows[4].panels.should.be.length_of(1)

        generated_dashboard.rows[5].title.should.eql("Dead Letter Queues")
        generated_dashboard.rows[5].panels.should.be.length_of(1)

    def test_should_generate_lambda_sns_sqs_fifo_dashboard(self):
        lambda_name = "lambda-1"
        cloudwatch_data_source = "cloudwatch"
        lambda_insights_namespace = "insights"
        environment = "alpha"
        topics = ["topic-1", "topic-2"]
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "cloudwatch_data_source": cloudwatch_data_source,
            "lambda_insights_namespace": lambda_insights_namespace,
            "notifications": [],
            "fifo": True,
            "topics": topics,
        }

        generated_dashboard = lambda_sns_sqs_dashboard(**call_args)
        generated_dashboard.should.be.a(Dashboard)
        print(dir(generated_dashboard))
        generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
        sorted(generated_dashboard.tags).should.eql(
            sorted(["lambda", environment, "sqs", "sns", "fifo"])
        )
        generated_dashboard.rows.should.be.length_of(6)
        generated_dashboard.rows[0].panels.should.be.length_of(len(topics))
        generated_dashboard.rows[0].title.should.eql("SNS Topics")

        generated_dashboard.rows[1].title.should.eql("Invocations")
        generated_dashboard.rows[1].panels.should.be.length_of(2)

        generated_dashboard.rows[2].title.should.eql("Memory Utilization")
        generated_dashboard.rows[2].panels.should.be.length_of(2)

        generated_dashboard.rows[3].title.should.eql("Logs")
        generated_dashboard.rows[3].panels.should.be.length_of(1)

        generated_dashboard.rows[4].title.should.eql("Queues")
        generated_dashboard.rows[4].panels.should.be.length_of(1)

        generated_dashboard.rows[5].title.should.eql("Dead Letter Queues")
        generated_dashboard.rows[5].panels.should.be.length_of(1)
