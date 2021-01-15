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
from lib.lambdas import lambda_generate_graph
from lib import colors

from typing import List

# https://docs.aws.amazon.com/step-functions/latest/dg/procedure-cw-metrics.html

NAMESPACE = "AWS/States"
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
    name: str, cloudwatch_data_source: str, notifications: List[str], *args, **kwargs
):
    """
    Generate step function graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias=DURATION_MINIMUM_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionTime",
            statistics=["Minimum"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=DURATION_AVERAGE_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionTime",
            statistics=["Average"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=DURATION_MAXIMUM_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionTime",
            statistics=["Maximum"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_STARTED_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionsStarted",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_SUCCEEDED_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionsSucceeded",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_ABORTED_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionsAborted",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
            refId=SFN_EXECUTIONS_ABORTED_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_FAILED_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionsFailed",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
            refId=SFN_EXECUTIONS_FAILED_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_THROTTLED_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionsThrottled",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
            refId=SFN_EXECUTIONS_THROTTLED_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_TIMEDOUT_ALIAS,
            namespace=NAMESPACE,
            period="1m",
            metricName="ExecutionsTimedOut",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
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
        dataSource=cloudwatch_data_source,
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
    cloudwatch_data_source: str,
    influxdb_data_source: str,
    notifications: List[str],
    environment: str,
    lambdas: List[str],
    *args,
    **kwargs
):
    """Create a dashboard for the step function"""

    tags = ["step-function", environment]

    if not name.startswith("arn:aws:states"):
        raise Exception("Statemachine ARN should be provided")

    sfn_name = name.split(":")[-1]

    sfn_graph = generate_sfn_graph(
        name=sfn_name,
        cloudwatch_data_source=cloudwatch_data_source,
        notifications=notifications,
    )

    rows = [Row(panels=[sfn_graph])]

    if lambdas:
        tags = tags + ["lambda"]

        lambda_graphs = [
            lambda_generate_graph(
                name=l, cloudwatch_data_source=cloudwatch_data_source, notifications=[]
            )
            for l in lambdas
        ]

        lambda_rows = [Row(panels=[g]) for g in lambda_graphs]

        rows = rows + lambda_rows

    return Dashboard(
        title="{}{}".format(SFN_DASHBOARD_PREFIX, sfn_name),
        editable=EDITABLE,
        annotations=get_release_annotations(influxdb_data_source),
        templating=get_release_templating(influxdb_data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
    ).auto_panel_ids()
