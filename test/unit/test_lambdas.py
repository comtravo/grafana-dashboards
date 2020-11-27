from grafanalib.core import Alert, AlertCondition, Dashboard, Graph, Target
from grafanalib.influxdb import InfluxDBTarget
from lib.lambdas import (
    dispatcher,
    lambda_generate_graph,
    lambda_cron_dashboard,
    lambda_events_dashboard,
    lambda_cognito_dashboard,
    lambda_logs_dashboard,
    create_lambda_sqs_dlq_graph,
    create_lambda_sqs_graph,
    lambda_sqs_dashboard,
    lambda_sns_sqs_dashboard,
)

import re


class TestDispatcher:
    def test_should_throw_exception_when_dispatcher_called_with_wrong_arguments(self):
        dispatcher.when.called_with(service="foo", trigger="bar").should.throw(
            Exception, r"dispatcher recieved a non l"
        )

    def test_should_call_trigger_handlers(self):
        expected_triggers = ["cognito", "cron", "events", "logs", "sns", "sqs"]

        for trigger in expected_triggers:
            dispatcher.when.called_with(service="lambda", trigger=trigger).should.be.ok

    def test_should_generate_lambda_graph(self):
        lambda_name = "lambda-1"
        data_source = "influxdb"
        expected_queries = [
            'SELECT min("duration_minimum") FROM "autogen"."cloudwatch_aws_lambda" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(null)'.format(
                lambda_name
            ),
            'SELECT mean("duration_average") FROM "autogen"."cloudwatch_aws_lambda" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(null)'.format(
                lambda_name
            ),
            'SELECT max("duration_maximum") FROM "autogen"."cloudwatch_aws_lambda" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(null)'.format(
                lambda_name
            ),
            'SELECT max("invocations_sum") FROM "autogen"."cloudwatch_aws_lambda" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                lambda_name
            ),
            'SELECT max("errors_sum") FROM "autogen"."cloudwatch_aws_lambda" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                lambda_name
            ),
        ]
        generated_lambd_graph = lambda_generate_graph(
            name=lambda_name, data_source=data_source, notifications=[]
        )
        generated_lambd_graph.should.be.a(Graph)
        generated_lambd_graph.should.have.property("title").with_value.equal(
            "Lambda: {}".format(lambda_name)
        )
        generated_lambd_graph.should.have.property("dataSource").with_value.equal(
            data_source
        )
        generated_lambd_graph.should.have.property("alert").with_value.equal(None)
        generated_lambd_graph.should.have.property("targets")
        generated_lambd_graph.targets.should.have.length_of(5)
        for target in generated_lambd_graph.targets:
            target.query.should.be.within(expected_queries)

    def test_should_generate_lambda_graph_with_alert_notifications(self):
        lambda_name = "lambda-1"
        data_source = "influxdb"
        notifications = ["lorem", "ipsum"]

        expected_alert_query = InfluxDBTarget(
            alias="Errors - Sum",
            query='SELECT max("errors_sum") FROM "autogen"."cloudwatch_aws_lambda" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                lambda_name
            ),
            rawQuery=True,
            refId="A",
        )

        generated_lambd_graph = lambda_generate_graph(
            name=lambda_name, data_source=data_source, notifications=notifications
        )
        generated_lambd_graph.should.have.property("alert").be.a(Alert)
        generated_lambd_graph.alert.executionErrorState.should.eql("alerting")
        generated_lambd_graph.alert.noDataState.should.eql("keep_state")
        generated_lambd_graph.alert.alertConditions.should.have.length_of(1)
        generated_lambd_graph.alert.alertConditions[0].should.be.a(AlertCondition)
        generated_lambd_graph.alert.alertConditions[0].target.should.eql(
            Target(refId="A")
        )
        generated_lambd_graph.targets.should.contain(expected_alert_query)

    def test_should_generate_lambda_basic_dashboards(self):
        lambda_name = "lambda-1"
        data_source = "influxdb"
        environment = "alpha"
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "data_source": data_source,
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
            generated_dashboard.tags.sort().should.eql(
                ["lambda", environment, expected_dashboard_tag].sort()
            )

    def test_should_create_lambda_sqs_dlq_graph(self):
        lambda_name = "lambda-1"
        data_source = "influxdb"
        notifications = ["lorem"]

        expected_alert_query = InfluxDBTarget(
            alias="Approximate number of messages available",
            query='SELECT max("approximate_number_of_messages_visible_maximum") FROM "autogen"."cloudwatch_aws_sqs" WHERE ("queue_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                lambda_name
            ),
            rawQuery=True,
            refId="A",
        )
        generated_lambd_graph = create_lambda_sqs_dlq_graph(
            name=lambda_name, data_source=data_source, notifications=notifications
        )
        generated_lambd_graph.should.be.a(Graph)
        generated_lambd_graph.should.have.property("title").with_value.equal(
            "SQS Dead Letter Queue: {}".format(lambda_name)
        )
        generated_lambd_graph.should.have.property("dataSource").with_value.equal(
            data_source
        )
        generated_lambd_graph.should.have.property("targets")
        generated_lambd_graph.targets.should.have.length_of(1)
        generated_lambd_graph.targets[0].should.eql(expected_alert_query)
        generated_lambd_graph.should.have.property("alert").be.a(Alert)
        generated_lambd_graph.alert.executionErrorState.should.eql("alerting")
        generated_lambd_graph.alert.noDataState.should.eql("keep_state")

    def test_should_create_lambda_sqs_graph(self):
        lambda_name = "lambda-1"
        data_source = "influxdb"

        expected_query = InfluxDBTarget(
            alias="Number of messages sent to the queue",
            query='SELECT max("number_of_messages_sent_sum") FROM "autogen"."cloudwatch_aws_sqs" WHERE ("queue_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                lambda_name
            ),
            rawQuery=True,
            refId="A",
        )
        generated_lambd_graph = create_lambda_sqs_graph(
            name=lambda_name, data_source=data_source
        )
        generated_lambd_graph.should.be.a(Graph)
        generated_lambd_graph.should.have.property("title").with_value.equal(
            "SQS: {}".format(lambda_name)
        )
        generated_lambd_graph.should.have.property("dataSource").with_value.equal(
            data_source
        )
        generated_lambd_graph.should.have.property("targets")
        generated_lambd_graph.targets.should.have.length_of(1)
        generated_lambd_graph.targets[0].should.eql(expected_query)

    def test_should_generate_lambda_sqs_dashboard(self):
        lambda_name = "lambda-1"
        data_source = "influxdb"
        environment = "alpha"
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "data_source": data_source,
            "notifications": [],
        }

        generated_dashboard = lambda_sqs_dashboard(**call_args)
        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
        generated_dashboard.tags.sort().should.eql(
            ["lambda", environment, "sqs"].sort()
        )
        generated_dashboard.rows.should.be.length_of(3)

    def test_should_generate_lambda_sns_sqs_dashboard(self):
        lambda_name = "lambda-1"
        data_source = "influxdb"
        environment = "alpha"
        topics = ["topic-1", "topic-2"]
        call_args = {
            "name": lambda_name,
            "environment": environment,
            "data_source": data_source,
            "notifications": [],
            "topics": topics,
        }

        generated_dashboard = lambda_sns_sqs_dashboard(**call_args)
        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.eql("Lambda: {}".format(lambda_name))
        generated_dashboard.tags.sort().should.eql(
            ["lambda", environment, "sqs", "sns"].sort()
        )
        generated_dashboard.rows.should.be.length_of(4)
        generated_dashboard.rows[0].panels.should.be.length_of(len(topics))
