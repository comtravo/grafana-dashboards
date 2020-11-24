from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    MILLISECONDS_FORMAT,
    OP_AND,
    RTYPE_MAX,
    SHORT_FORMAT,
    TimeRange,
    Row,
    Target,
    YAxes,
    YAxis,
)
from grafanalib.influxdb import InfluxDBTarget

from lib.annotations import get_release_annotations
from lib.templating import get_release_template
from lib import colors

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
        "cognito": lambda_cron_dashboard,
        "cron": lambda_cron_dashboard,
        "events": lambda_cron_dashboard,
        "logs": lambda_cron_dashboard,
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
        transparent=True,
        editable=False,
        alert=alert,
    ).auto_ref_ids()


def lambda_cron_dashboard(
    name: str, data_source: str, alert: bool, environment: str, *args, **kwargs
):
    """
    Generate lambda dashboard for cron
    """
    return Dashboard(
        title=name,
        editable=False,
        annotations=get_release_annotations(data_source),
        templating=get_release_template(data_source),
        tags=["lambda", "cron", environment],
        timezone="",
        sharedCrosshair=True,
        rows=[
            Row(panels=[lambda_generate_graph(name, data_source, create_alert=alert)])
        ],
    ).auto_panel_ids()
