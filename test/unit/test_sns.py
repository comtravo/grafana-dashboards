from grafanalib.core import Alert, AlertCondition, Graph, Target
from grafanalib.cloudwatch import CloudwatchMetricsTarget
from lib.sns import create_sns_graph


class TestCreateSNSGraph:
    def test_should_generate_correct_object_with_alert_notifications(self):

        expected_data_source = "prod"
        expected_topic_name = "sns-1"
        expected_title = "SNS: sns-1"
        expected_notifications = ["slack-1"]
        expected_targets = [
            CloudwatchMetricsTarget(
                statistics=["Sum"],
                metricName="NumberOfMessagesPublished",
                dimensions={"TopicName": expected_topic_name},
            ),
            CloudwatchMetricsTarget(
                statistics=["Sum"],
                metricName="NumberOfNotificationsDelivered",
                dimensions={"TopicName": expected_topic_name},
            ),
            CloudwatchMetricsTarget(
                statistics=["Sum"],
                metricName="NumberOfMessagesFailed",
                dimensions={"TopicName": expected_topic_name},
            ),
        ]

        actual_sns_graph = create_sns_graph(
            name=expected_topic_name,
            cloudwatch_data_source=expected_data_source,
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
        ).which.should.be.equal("no_data")
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
            target.should.be.a(CloudwatchMetricsTarget)
            target.namespace.should.be.equal("AWS/SNS")
            target.period.should.be.equal("5m")
            target.statistics.should.be.equal(["Sum"])
            target.dimensions.should.be.equal({"TopicName": expected_topic_name})
            target.metricName.should.be.within(
                [
                    "NumberOfMessagesPublished",
                    "NumberOfNotificationsDelivered",
                    "NumberOfMessagesFailed",
                ]
            )

        actual_sns_graph.targets[2].refId.should.be.equal("A")

    def test_should_generate_correct_object_with_no_alert_notifications(self):

        expected_data_source = "prod"
        expected_topic_name = "sns-1"
        expected_notifications = []

        actual_sns_graph = create_sns_graph(
            name=expected_topic_name,
            cloudwatch_data_source=expected_data_source,
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

        actual_sns_graph = create_sns_graph(
            name=sns_topic_arn,
            cloudwatch_data_source=expected_data_source,
            notifications=[],
        )
        actual_sns_graph.should.be.a(Graph)
        actual_sns_graph.should.have.property("title").with_value.equal(expected_title)
        actual_sns_graph.targets.should.have.length_of(3)
        for target in actual_sns_graph.targets:
            target.dimensions.should.equal({"TopicName": expected_topic_name})
