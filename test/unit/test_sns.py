from grafanalib.core import Alert, Graph
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

        actual_sns_graph = create_sns_graph(
            name=expected_topic_name,
            data_source=expected_data_source,
            notifications=expected_notifications,
        )
        actual_sns_graph.should.be.a(Graph)
        print(dir(actual_sns_graph))
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

        actual_sns_graph.should.have.property("targets").length_of(3)

        for target in actual_sns_graph.targets:
            target.should.be.a(InfluxDBTarget)
            target.query.should.be.within(expected_queries)
