from grafanalib.core import (
    Dashboard,
    Graph,
    Row,
    YAxes,
    YAxis,
    MILLISECONDS_FORMAT,
    SHORT_FORMAT,
    single_y_axis,
)
from grafanalib.influxdb import InfluxDBTarget

MEASUREMENT = "cloudwatch_aws_lambda"
RETENTION_POLICY = "autogen"
RAW_QUERY = True

DURATION_MINIMUM_ALIAS = "Duration - Minimum"
DURATION_AVERGAE_ALIAS = "Duration - Average"
DURATION_MAXIMUM_ALIAS = "Duration - Maximum"
INVOCATIONS_ALIAS = "Invocations - Sum"
ERRORS_ALIAS = "Errors - Sum"


def dispatcher(service, trigger, *args, **kwargs):
    """
    lambda dashboard generator
    """
    pass


def lambda_cron_graph_generate(
    name: str, dataSource: str, alert: bool, *args, **kwargs
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
            refId="A",
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
            "color": "#37872D",
        },
        {
            "alias": ERRORS_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": "#C4162A",
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

    return Graph(
        title=name,
        dataSource=dataSource,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=True,
        editable=False,
    ).auto_ref_ids()


def lambda_cron_dashboard(
    name: str, dataSource: str, alert: bool, environment: str, *args, **kwargs
):
    """
    Generate lambda dashboard for cron
    """
    return Dashboard(
        title=name,
        editable=False,
        tags=["lambda", "cron", environment],
        rows=[Row(panels=[lambda_cron_graph_generate(name, dataSource, alert)])],
    ).auto_panel_ids()
