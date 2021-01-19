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
from grafanalib.cloudwatch import CloudwatchMetricsTarget

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
from lib.templating import get_release_templating
from lib import colors
from typing import List

import re

NAMESPACE = "AWS/SNS"
PERIOD = "5m"

SNS_PUBLISHED_NOTIFICATIONS = "Published"
SNS_DELIVERED_NOTIFICATIONS = "Delivered"
SNS_FAILED_NOTIFICATIONS = "Failed"


def create_sns_graph(name: str, cloudwatch_data_source: str, notifications: List[str]):
    """Create SNS graph"""

    if re.match("^arn:aws:sns", name):
        name = name.split(":")[-1]

    targets = [
        CloudwatchMetricsTarget(
            alias=SNS_PUBLISHED_NOTIFICATIONS,
            namespace=NAMESPACE,
            period=PERIOD,
            statistics=["Sum"],
            metricName="NumberOfMessagesPublished",
            dimensions={"TopicName": name},
        ),
        CloudwatchMetricsTarget(
            alias=SNS_DELIVERED_NOTIFICATIONS,
            namespace=NAMESPACE,
            period=PERIOD,
            statistics=["Sum"],
            metricName="NumberOfNotificationsDelivered",
            dimensions={"TopicName": name},
        ),
        CloudwatchMetricsTarget(
            alias=SNS_FAILED_NOTIFICATIONS,
            namespace=NAMESPACE,
            period=PERIOD,
            statistics=["Sum"],
            metricName="NumberOfMessagesFailed",
            dimensions={"TopicName": name},
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
        dataSource=cloudwatch_data_source,
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
