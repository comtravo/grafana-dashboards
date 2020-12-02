from grafanalib.core import Alert, AlertCondition, Graph, Target
from grafanalib.influxdb import InfluxDBTarget
from lib.sns import create_sns_graph


class TestCreateSNSGraph:
    def test_should_generate_correct_object_with_alert_notifications(self):

        expected_data_source = "prod"
        expected_topic_name = "sns-1"
        expected_title = "SNS: sns-1"
        expected_notifications = ["slack-1"]
        expected_queries = [
            'SELECT sum("number_of_messages_published_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
            'SELECT sum("number_of_notifications_delivered_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
            'SELECT sum("number_of_notifications_failed_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
        ]

        expected_alert_query = InfluxDBTarget(
            alias="Failed notifications",
            query='SELECT sum("number_of_notifications_failed_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
            rawQuery=True,
            refId="A",
        )

        actual_sns_graph = create_sns_graph(
            name=expected_topic_name,
            data_source=expected_data_source,
            notifications=expected_notifications,
        )
        actual_sns_graph.should.be.a(Graph)
        actual_sns_graph.should.have.property("title").with_value.equal(expected_title)
        actual_sns_graph.should.have.property("bars").with_value.equal(True)
        actual_sns_graph.should.have.property("lines").with_value.equal(False)

        actual_sns_graph.should.have.property("alert").a(Alert)
        actual_sns_graph.alert.should.have.property(
            "executionErrorState"
        ).which.should.be.equal("alerting")
        actual_sns_graph.alert.should.have.property(
            "noDataState"
        ).which.should.be.equal("keep_state")
        actual_sns_graph.alert.should.have.property(
            "notifications"
        ).which.should.be.equal(expected_notifications)
        actual_sns_graph.alert.should.have.property(
            "alertConditions"
        ).which.should.have.length_of(1)
        actual_sns_graph.alert.alertConditions[0].should.be.a(AlertCondition)
        actual_sns_graph.alert.alertConditions[0].should.have.property("target")
        actual_sns_graph.alert.alertConditions[0].target.should.be.equal(
            Target(refId="A")
        )

        actual_sns_graph.should.have.property("targets").length_of(3)

        for target in actual_sns_graph.targets:
            target.should.be.a(InfluxDBTarget)
            target.query.should.be.within(expected_queries)

        actual_sns_graph.targets.should.contain(expected_alert_query)

    def test_should_generate_correct_object_with_no_alert_notifications(self):

        expected_data_source = "prod"
        expected_topic_name = "sns-1"
        expected_notifications = []

        actual_sns_graph = create_sns_graph(
            name=expected_topic_name,
            data_source=expected_data_source,
            notifications=expected_notifications,
        )
        actual_sns_graph.should.have.property("alert").with_value.equal(None)

    def test_should_generate_correct_object_when_arn_of_sns_topic_is_passed(self):

        expected_data_source = "prod"
        sns_topic_arn = (
            "arn:aws:sns:eu-west-1:1234567890:lambda-elasticsearch-booking-alpha"
        )
        expected_topic_name = "lambda-elasticsearch-booking-alpha"
        expected_title = "SNS: lambda-elasticsearch-booking-alpha"
        expected_notifications = ["slack-1"]
        expected_queries = [
            'SELECT sum("number_of_messages_published_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
            'SELECT sum("number_of_notifications_delivered_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
            'SELECT sum("number_of_notifications_failed_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
        ]

        expected_alert_query = InfluxDBTarget(
            alias="Failed notifications",
            query='SELECT sum("number_of_notifications_failed_sum") FROM "autogen"."cloudwatch_aws_sns" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                expected_topic_name
            ),
            rawQuery=True,
            refId="A",
        )

        actual_sns_graph = create_sns_graph(
            name=sns_topic_arn,
            data_source=expected_data_source,
            notifications=expected_notifications,
        )
        actual_sns_graph.should.be.a(Graph)
        actual_sns_graph.should.have.property("title").with_value.equal(expected_title)
        actual_sns_graph.should.have.property("bars").with_value.equal(True)
        actual_sns_graph.should.have.property("lines").with_value.equal(False)

        actual_sns_graph.should.have.property("alert").a(Alert)
        actual_sns_graph.alert.should.have.property(
            "executionErrorState"
        ).which.should.be.equal("alerting")
        actual_sns_graph.alert.should.have.property(
            "noDataState"
        ).which.should.be.equal("keep_state")
        actual_sns_graph.alert.should.have.property(
            "notifications"
        ).which.should.be.equal(expected_notifications)
        actual_sns_graph.alert.should.have.property(
            "alertConditions"
        ).which.should.have.length_of(1)
        actual_sns_graph.alert.alertConditions[0].should.be.a(AlertCondition)
        actual_sns_graph.alert.alertConditions[0].should.have.property("target")
        actual_sns_graph.alert.alertConditions[0].target.should.be.equal(
            Target(refId="A")
        )

        actual_sns_graph.should.have.property("targets").length_of(3)

        for target in actual_sns_graph.targets:
            target.should.be.a(InfluxDBTarget)
            target.query.should.be.within(expected_queries)

        actual_sns_graph.targets.should.contain(expected_alert_query)
