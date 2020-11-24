from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
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
SNS_ACTIVE_SUBSCRIPTIONS = "Active subscriptions"

SNS_FAILED_DELIVERIES_REF_ID = "B"


def create_lambda_sns_graph(name: str, data_source: str, create_alert: bool):
    """Create SNS graph"""

    targets = [
        InfluxDBTarget(
            alias=SNS_PUBLISHED_NOTIFICATIONS,
            query='SELECT sum("number_of_messages_published_sum") FROM "{}"."{}" WHERE ("topic_name" = \'{}\') GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, SNS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=SNS_DELIVERED_NOTIFICATIONS,
            query='SELECT sum("number_of_notifications_delivered_sum") FROM "{}"."{}" WHERE ("topic_name" = \'{}\') GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, SNS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=SNS_FAILED_NOTIFICATIONS,
            query='SELECT sum("number_of_notifications_failed_sum") FROM "{}"."{}" WHERE ("topic_name" = \'{}\') GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, SNS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=SNS_FAILED_DELIVERIES_REF_ID if create_alert else None,
        ),
        InfluxDBTarget(
            alias=SNS_ACTIVE_SUBSCRIPTIONS,
            query='SELECT (sum("number_of_notifications_delivered_sum") / sum("number_of_messages_published_sum")) FROM "{}"."{}" WHERE ("topic_name" = \'{}\') GROUP BY time(10m) fill(previous)'.format(
                RETENTION_POLICY, SNS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID if create_alert else None,
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
        {
            "alias": SNS_ACTIVE_SUBSCRIPTIONS,
            "hiddenSeries": True,
            "legend": False,
        },
    ]

    yAxes = single_y_axis(format=SHORT_FORMAT)
    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )

    alert = None

    if create_alert:
        alert = Alert(
            name="{} alerts".format(name),
            message="{} seems to have no subscriptions or failed deliveries".format(
                name
            ),
            noDataState="alerting",
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
                AlertCondition(
                    Target(refId=SNS_FAILED_DELIVERIES_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
            ],
        )

    return Graph(
        title=name,
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
