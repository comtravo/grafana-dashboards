"""
Generate SNS dashboards and alerts
"""

import re
from typing import List

from grafanalib.core import (
    Alert,
    AlertCondition,
    Graph,
    GreaterThan,
    OP_OR,
    RTYPE_MAX,
    single_y_axis,
    SHORT_FORMAT,
    TimeRange,
    Target,
)
from grafanalib.influxdb import InfluxDBTarget

from lib.commons import (
    ALERT_REF_ID,
    ALERT_THRESHOLD,
    EDITABLE,
    RAW_QUERY,
    RETENTION_POLICY,
    TRANSPARENT,
)
from lib import colors

SNS_MEASUREMENT = "cloudwatch_aws_sns"

SNS_PUBLISHED_NOTIFICATIONS = "Published"
SNS_DELIVERED_NOTIFICATIONS = "Delivered"
SNS_FAILED_NOTIFICATIONS = "Failed"


def create_sns_graph(name: str, data_source: str, notifications: List[str]):
    """Create SNS graph"""

    if re.match("^arn:aws:sns", name):
        name = name.split(":")[-1]

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

    series_overrides = [
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

    y_axes = single_y_axis(format=SHORT_FORMAT)

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
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
            ],
            frequency="2m",
            gracePeriod="2m",
            notifications=notifications,
        )

    return Graph(
        title="SNS: {}".format(name),
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()
