from grafanalib.core import Alert, AlertCondition, Dashboard, Graph, Target
from grafanalib.influxdb import InfluxDBTarget
from lib.lambdas import dispatcher, lambda_generate_graph

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
