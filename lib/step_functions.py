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
from lib.lambdas import lambda_generate_graph
from lib import colors

from typing import List

# https://docs.aws.amazon.com/step-functions/latest/dg/procedure-cw-metrics.html

SFN_MEASUREMENT = "cloudwatch_aws_states"
SFN_DASHBOARD_PREFIX = "Step Function: "

DURATION_MINIMUM_ALIAS = "Duration - Minimum"
DURATION_AVERAGE_ALIAS = "Duration - Average"
DURATION_MAXIMUM_ALIAS = "Duration - Maximum"

SFN_EXECUTIONS_STARTED_ALIAS = "Executions - Started"
SFN_EXECUTIONS_SUCCEEDED_ALIAS = "Executions - Succeeded"
SFN_EXECUTIONS_ABORTED_ALIAS = "Executions - Aborted"
SFN_EXECUTIONS_ABORTED_REF_ID = "A"
SFN_EXECUTIONS_FAILED_ALIAS = "Executions - Failed"
SFN_EXECUTIONS_FAILED_REF_ID = "B"
SFN_EXECUTIONS_THROTTLED_ALIAS = "Executions - Throttled"
SFN_EXECUTIONS_THROTTLED_REF_ID = "C"
SFN_EXECUTIONS_TIMEDOUT_ALIAS = "Executions - Timeout"
SFN_EXECUTIONS_TIMEDOUT_REF_ID = "D"


def generate_sfn_graph(
    name: str, data_source: str, notifications: List[str], *args, **kwargs
):
    """
    Generate step function graph
    """

    targets = [
        InfluxDBTarget(
            alias=DURATION_MINIMUM_ALIAS,
            query='SELECT min("execution_time_minimum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=DURATION_AVERAGE_ALIAS,
            query='SELECT mean("execution_time_average") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=DURATION_MAXIMUM_ALIAS,
            query='SELECT max("execution_time_maximum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=SFN_EXECUTIONS_STARTED_ALIAS,
            query='SELECT max("executions_started_sum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=SFN_EXECUTIONS_SUCCEEDED_ALIAS,
            query='SELECT max("executions_succeeded_sum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=SFN_EXECUTIONS_ABORTED_ALIAS,
            query='SELECT max("executions_aborted_sum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=SFN_EXECUTIONS_ABORTED_REF_ID,
        ),
        InfluxDBTarget(
            alias=SFN_EXECUTIONS_FAILED_ALIAS,
            query='SELECT max("executions_failed_sum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=SFN_EXECUTIONS_FAILED_REF_ID,
        ),
        InfluxDBTarget(
            alias=SFN_EXECUTIONS_THROTTLED_ALIAS,
            query='SELECT max("execution_throttled_sum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=SFN_EXECUTIONS_THROTTLED_REF_ID,
        ),
        InfluxDBTarget(
            alias=SFN_EXECUTIONS_TIMEDOUT_ALIAS,
            query='SELECT max("execution_timed_out_sum") FROM "{}"."{}" WHERE ("state_machine_arn" = \'{}\') AND $timeFilter GROUP BY time(1m) fill(0)'.format(
                RETENTION_POLICY, SFN_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=SFN_EXECUTIONS_TIMEDOUT_REF_ID,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=MILLISECONDS_FORMAT, decimals=2),
        YAxis(format=SHORT_FORMAT, decimals=2),
    )

    seriesOverrides = [
        {
            "alias": SFN_EXECUTIONS_STARTED_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.BLUE,
            "zindex": -2,
        },
        {
            "alias": SFN_EXECUTIONS_SUCCEEDED_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.GREEN,
            "zindex": -1,
        },
        {
            "alias": SFN_EXECUTIONS_ABORTED_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.RED,
        },
        {
            "alias": SFN_EXECUTIONS_FAILED_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.RED,
        },
        {
            "alias": SFN_EXECUTIONS_THROTTLED_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.ORANGE,
        },
        {
            "alias": SFN_EXECUTIONS_TIMEDOUT_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.RED,
        },
        {"alias": DURATION_MINIMUM_ALIAS, "color": "#C8F2C2", "lines": False},
        {"alias": DURATION_AVERAGE_ALIAS, "color": "#FADE2A", "fill": 0},
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
            name="{} execution issues".format(name),
            message="{} might have failed, aborted, throttled or timedout".format(name),
            executionErrorState="alerting",
            noDataState="keep_state",
            alertConditions=[
                AlertCondition(
                    Target(refId=SFN_EXECUTIONS_ABORTED_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
                AlertCondition(
                    Target(refId=SFN_EXECUTIONS_FAILED_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
                AlertCondition(
                    Target(refId=SFN_EXECUTIONS_THROTTLED_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
                AlertCondition(
                    Target(refId=SFN_EXECUTIONS_TIMEDOUT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
            ],
            gracePeriod="2m",
            frequency="2m",
            notifications=notifications,
        )

    return Graph(
        title="Step function execution metrics",
        dataSource=data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def generate_sfn_dashboard(
    name: str,
    data_source: str,
    notifications: List[str],
    environment: str,
    lambdas: List[str],
    *args,
    **kwargs
):
    """Create a dashboard for the step function"""

    tags = ["step-function", environment]

    if lambdas:
        tags = tags + ["lambda"]

    sfn_graph = generate_sfn_graph(
        name=name, data_source=data_source, notifications=notifications
    )

    lambda_panels = [
        lambda_generate_graph(
            name=l, data_source=data_source, notifications=notifications
        )
        for l in lambdas
    ]

    rows = [Row(panels=[sfn_graph])]

    if lambda_panels:
        rows = rows + [Row(panels=lambda_panels)]

    return Dashboard(
        title="{}{}".format(SFN_DASHBOARD_PREFIX, name),
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_template(data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
    ).auto_panel_ids()
