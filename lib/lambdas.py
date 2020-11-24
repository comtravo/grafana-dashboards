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
    ALERT_THRESHOLD,
    EDITABLE,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)
from lib.templating import get_release_template
from lib import colors

from typing import List

MEASUREMENT = "cloudwatch_aws_lambda"
RETENTION_POLICY = "autogen"
RAW_QUERY = True

ALERT_REF_ID = "A"

DURATION_MINIMUM_ALIAS = "Duration - Minimum"
DURATION_AVERGAE_ALIAS = "Duration - Average"
DURATION_MAXIMUM_ALIAS = "Duration - Maximum"
INVOCATIONS_ALIAS = "Invocations - Sum"
ERRORS_ALIAS = "Errors - Sum"


def dispatcher(service, trigger, *args, **kwargs):
    """
    lambda dashboard generator
    """

    if service != "lambda":
        raise Exception("Lambda dispatcher recieved a non lambda call")

    dispatch = {
        "cognito": lambda_cognito_dashboard,
        "cron": lambda_cron_dashboard,
        "events": lambda_events_dashboard,
        "logs": lambda_cron_dashboard,
        "sqs": lambda_sqs_dashboard,
    }

    return dispatch[trigger](**kwargs)


def lambda_generate_graph(
    name: str, data_source: str, create_alert: bool, *args, **kwargs
):
    """
    Generate lambda cron graph
    """

    targets = [
        InfluxDBTarget(
            alias=DURATION_MINIMUM_ALIAS,
            query='SELECT min("duration_minimum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') GROUP BY time(5m) fill(null)'.format(
                RETENTION_POLICY, MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=DURATION_AVERGAE_ALIAS,
            query='SELECT mean("duration_average") FROM "{}"."{}" WHERE ("function_name" = \'{}\') GROUP BY time(5m) fill(null)'.format(
                RETENTION_POLICY, MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=DURATION_MAXIMUM_ALIAS,
            query='SELECT max("duration_maximum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') GROUP BY time(5m) fill(null)'.format(
                RETENTION_POLICY, MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=INVOCATIONS_ALIAS,
            query='SELECT max("invocations_sum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') GROUP BY time(1m) fill(null)'.format(
                RETENTION_POLICY, MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=ERRORS_ALIAS,
            query='SELECT max("errors_sum") FROM "{}"."{}" WHERE ("function_name" = \'{}\') GROUP BY time(1m) fill(null)'.format(
                RETENTION_POLICY, MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID if create_alert else None,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=MILLISECONDS_FORMAT, decimals=2),
        YAxis(format=SHORT_FORMAT, decimals=2),
    )

    seriesOverrides = [
        {
            "alias": INVOCATIONS_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.GREEN,
        },
        {
            "alias": ERRORS_ALIAS,
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

    if create_alert:
        alert = Alert(
            name="{} Invocation Errors".format(name),
            message="{} is having invocation errors".format(name),
            noDataState="alerting",
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
        )

    return Graph(
        title=name,
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
    alert: bool,
    environment: str,
    *args,
    **kwargs
):
    """Create a dashboard with just the lambda

    Args:
        tags (list): List of tags to apply to the dasboard
    """

    return Dashboard(
        title=name,
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_template(data_source),
        tags=tags + ["lambda", environment],
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(panels=[lambda_generate_graph(name, data_source, create_alert=alert)])
        ],
    ).auto_panel_ids()


def create_lambda_sqs_graph(name: str, data_source: str, create_alert: bool):
    """Create SQS graph"""

    targets = [
        InfluxDBTarget(
            alias="Approximate number of messages available",
            query='SELECT max("approximate_number_of_messages_visible_maximum") FROM "{}"."cloudwatch_aws_sqs" WHERE ("queue_name" = \'{}\') GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID if create_alert else None,
        )
    ]

    yAxes = single_y_axis(format=SHORT_FORMAT)
    alert = None

    if create_alert:
        alert = Alert(
            name="{} messages".format(name),
            message="{} is having messages".format(name),
            noDataState="alerting",
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
        )

    return Graph(
        title=name,
        dataSource=data_source,
        targets=targets,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def lambda_sqs_dashboard(
    name: str, data_source: str, alert: bool, environment: str, *args, **kwargs
):
    """Create a dashboard with Lambda and its SQS dead letter queue"""
    tags = ["lambda", "sqs", environment]

    lambda_graph = lambda_generate_graph(name, data_source, create_alert=alert)
    dead_letter_sqs_graph = create_lambda_sqs_graph(
        name=name + "-dlq", data_source=data_source, create_alert=alert
    )

    return Dashboard(
        title=name,
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_template(data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[Row(panels=[lambda_graph]), Row(panels=[dead_letter_sqs_graph])],
    ).auto_panel_ids()
