from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    MILLISECONDS_FORMAT,
    OP_AND,
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
from lib.sns import create_sns_graph
from lib.templating import get_release_templating
from lib import colors

from typing import List

LAMBDA_MEASUREMENT = "cloudwatch_aws_lambda"
LAMBDA_DASHBOARD_PREFIX = "Lambda: "


DURATION_MINIMUM_ALIAS = "Duration - Minimum"
DURATION_AVERGAE_ALIAS = "Duration - Average"
DURATION_MAXIMUM_ALIAS = "Duration - Maximum"
LAMBDA_INVOCATIONS_ALIAS = "Invocations - Sum"
LAMBDA_ERRORS_ALIAS = "Errors - Sum"

LAMBDA_INVOCATION_METRIC_GROUP_BY = "1m"


def dispatcher(service, trigger, *args, **kwargs):
    """
    lambda dashboard generator
    """

    if service != "lambda":
        raise Exception("Lambda dispatcher recieved a non lambda call")

    dispatch = {
        "cognito-idp": lambda_cognito_dashboard,
        "cloudwatch-event-schedule": lambda_cron_dashboard,
        "cloudwatch-event-trigger": lambda_events_dashboard,
        "cloudwatch-logs": lambda_cron_dashboard,
        "sqs": lambda_sqs_dashboard,
        "sns": lambda_sns_sqs_dashboard,
        "null": lambda_basic_dashboard,
    }

    return dispatch[trigger](**kwargs)


def lambda_generate_graph(
    name: str, data_source: str, notifications: List[str], *args, **kwargs
):
    """
    Generate lambda graph
    """

    targets = [
        InfluxDBTarget(
            alias=DURATION_MINIMUM_ALIAS,
            query='SELECT min("duration_minimum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(null)'.format(
                RETENTION_POLICY, LAMBDA_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=DURATION_AVERGAE_ALIAS,
            query='SELECT mean("duration_average") FROM "{}"."{}" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(null)'.format(
                RETENTION_POLICY, LAMBDA_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=DURATION_MAXIMUM_ALIAS,
            query='SELECT max("duration_maximum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(null)'.format(
                RETENTION_POLICY, LAMBDA_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=LAMBDA_INVOCATIONS_ALIAS,
            query='SELECT max("invocations_sum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                RETENTION_POLICY, LAMBDA_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=LAMBDA_ERRORS_ALIAS,
            query='SELECT max("errors_sum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(null)'.format(
                RETENTION_POLICY, LAMBDA_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID if notifications else None,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=MILLISECONDS_FORMAT, decimals=2),
        YAxis(format=SHORT_FORMAT, decimals=2),
    )

    seriesOverrides = [
        {
            "alias": LAMBDA_INVOCATIONS_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.GREEN,
        },
        {
            "alias": LAMBDA_ERRORS_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.RED,
        },
        {"alias": DURATION_MINIMUM_ALIAS, "color": "#C8F2C2", "lines": False},
        {"alias": DURATION_AVERGAE_ALIAS, "color": "#FADE2A", "fill": 0},
        {
            "alias": DURATION_MAXIMUM_ALIAS,
            "color": "rgb(77, 159, 179)",
            "fillBelowTo": DURATION_MINIMUM_ALIAS,
            "lines": False,
        },
    ]

    alert = None

    # https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
    if notifications:
        alert = Alert(
            name="{} Invocation Errors".format(name),
            message="{} is having invocation errors".format(name),
            executionErrorState="alerting",
            noDataState="keep_state",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Lambda: {}".format(name),
        dataSource=data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def lambda_cron_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for cron
    """
    tags = ["cron"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_basic_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for cron
    """
    tags = []
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_cognito_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for Cognito
    """
    tags = ["cognito"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_events_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for Cloudwatch Events
    """
    tags = ["cloudwatch events"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def lambda_logs_dashboard(*args, **kwargs):
    """
    Generate lambda dashboard for Cloudwatch Logs
    """
    tags = ["cloudwatch logs"]
    return create_lambda_only_dashboard(tags, *args, **kwargs)


def create_lambda_only_dashboard(
    tags: List[str],
    name: str,
    data_source: str,
    notifications: List[str],
    environment: str,
    *args,
    **kwargs
):
    """Create a dashboard with just the lambda"""

    return Dashboard(
        title="{}{}".format(LAMBDA_DASHBOARD_PREFIX, name),
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_templating(data_source),
        tags=tags + ["lambda", environment],
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(
                panels=[
                    lambda_generate_graph(
                        name, data_source, notifications=notifications
                    )
                ]
            )
        ],
    ).auto_panel_ids()


def create_lambda_sqs_dlq_graph(name: str, data_source: str, notifications: List[str]):
    """Create SQS Deadletter graph"""

    targets = [
        InfluxDBTarget(
            alias="Approximate number of messages available",
            query='SELECT max("approximate_number_of_messages_visible_maximum") FROM "{}"."cloudwatch_aws_sqs" WHERE ("queue_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID if notifications else None,
        )
    ]

    yAxes = single_y_axis(format=SHORT_FORMAT)
    alert = None

    # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-monitoring-using-cloudwatch.html
    # https://aws.amazon.com/about-aws/whats-new/2019/12/amazon-sqs-now-supports-1-minute-cloudwatch-metrics/
    if notifications:
        alert = Alert(
            name="{} messages".format(name),
            message="{} is having messages".format(name),
            executionErrorState="alerting",
            noDataState="keep_state",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                ),
            ],
            gracePeriod="5m",
            notifications=notifications,
        )

    return Graph(
        title="SQS Dead Letter Queue: {}".format(name),
        dataSource=data_source,
        targets=targets,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def create_lambda_sqs_graph(name: str, data_source: str):
    """Create SQS graph"""

    targets = [
        InfluxDBTarget(
            alias="Number of messages sent to the queue",
            query='SELECT max("number_of_messages_sent_sum") FROM "{}"."cloudwatch_aws_sqs" WHERE ("queue_name" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, name
            ),
            rawQuery=RAW_QUERY,
        )
    ]

    yAxes = single_y_axis(format=SHORT_FORMAT)

    return Graph(
        title="SQS: {}".format(name),
        dataSource=data_source,
        targets=targets,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
    ).auto_ref_ids()


def lambda_sqs_dashboard(
    name: str,
    data_source: str,
    notifications: List[str],
    environment: str,
    *args,
    **kwargs
):
    """Create a dashboard with Lambda and its SQS dead letter queue"""
    tags = ["lambda", "sqs", environment]

    lambda_graph = lambda_generate_graph(name, data_source, notifications=notifications)
    sqs_graph = create_lambda_sqs_graph(name=name, data_source=data_source)
    dead_letter_sqs_graph = create_lambda_sqs_dlq_graph(
        name=name + "-dlq", data_source=data_source, notifications=notifications
    )

    return Dashboard(
        title="{}{}".format(LAMBDA_DASHBOARD_PREFIX, name),
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_templating(data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(panels=[lambda_graph]),
            Row(panels=[sqs_graph]),
            Row(panels=[dead_letter_sqs_graph]),
        ],
    ).auto_panel_ids()


def lambda_sns_sqs_dashboard(
    name: str,
    data_source: str,
    notifications: List[str],
    environment: str,
    topics: List[str],
    *args,
    **kwargs
):
    """Create a dashboard with Lambda, the SNS topics it is invoked from and its SQS dead letter queue"""
    tags = ["lambda", "sqs", environment, "sns"]

    lambda_graph = lambda_generate_graph(name, data_source, notifications=notifications)
    sqs_graph = create_lambda_sqs_graph(name=name, data_source=data_source)
    dead_letter_sqs_graph = create_lambda_sqs_dlq_graph(
        name=name + "-dlq", data_source=data_source, notifications=notifications
    )

    sns_topic_panels = [
        create_sns_graph(
            name=topic, data_source=data_source, notifications=notifications
        )
        for topic in topics
    ]

    return Dashboard(
        title="{}{}".format(LAMBDA_DASHBOARD_PREFIX, name),
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_templating(data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(panels=sns_topic_panels),
            Row(panels=[lambda_graph]),
            Row(panels=[sqs_graph]),
            Row(panels=[dead_letter_sqs_graph]),
        ],
    ).auto_panel_ids()
