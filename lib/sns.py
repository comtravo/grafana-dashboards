from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    LowerThan,
    MILLISECONDS_FORMAT,
    OP_OR,
    RTYPE_MAX,
    single_y_axis,
    SHORT_FORMAT,
    TimeRange,
    Row,
    Target,
    YAxes,
    YAxis,
)
from grafanalib.influxdb import InfluxDBTarget

from lib.annotations import get_release_annotations
from lib.commons import (
    ALERT_REF_ID,
    ALERT_THRESHOLD,
    EDITABLE,
    RAW_QUERY,
    RETENTION_POLICY,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)
from lib.templating import get_release_template
from lib import colors

from typing import List

SNS_MEASUREMENT = "cloudwatch_aws_sns"

SNS_PUBLISHED_NOTIFICATIONS = "Published notifications"
SNS_DELIVERED_NOTIFICATIONS = "Delivered notifications"
SNS_FAILED_NOTIFICATIONS = "Failed notifications"


def create_lambda_sns_graph(name: str, data_source: str, notifications: List[str]):
    """Create SNS graph"""

    targets = [
        InfluxDBTarget(
            alias=SNS_PUBLISHED_NOTIFICATIONS,
            query='SELECT sum("number_of_messages_published_sum") FROM "{}"."{}" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, SNS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=SNS_DELIVERED_NOTIFICATIONS,
            query='SELECT sum("number_of_notifications_delivered_sum") FROM "{}"."{}" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, SNS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=SNS_FAILED_NOTIFICATIONS,
            query='SELECT sum("number_of_notifications_failed_sum") FROM "{}"."{}" WHERE ("topic_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, SNS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID if notifications else None,
        ),
    ]

    seriesOverrides = [
        {
            "alias": SNS_FAILED_NOTIFICATIONS,
            "yaxis": 2,
            "color": colors.RED,
        },
        {
            "alias": SNS_PUBLISHED_NOTIFICATIONS,
            "zindex": 1,
        },
    ]

    yAxes = single_y_axis(format=SHORT_FORMAT)
    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )

    alert = None

    # https://docs.aws.amazon.com/sns/latest/dg/sns-monitoring-using-cloudwatch.html
    if notifications:
        alert = Alert(
            name="{} alerts".format(name),
            message="{} seems to have no subscriptions or failed deliveries".format(
                name
            ),
            executionErrorState="alerting",
            noDataState="keep_state",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
            ],
            gracePeriod="10m",
            notifications=notifications,
        )

    return Graph(
        title="SNS: {}".format(name),
        dataSource=data_source,
        targets=targets,
        yAxes=yAxes,
        seriesOverrides=seriesOverrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()
