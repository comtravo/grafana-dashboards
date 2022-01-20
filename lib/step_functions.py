from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    MILLISECONDS_FORMAT,
    OP_OR,
    RTYPE_MAX,
    SHORT_FORMAT,
    TimeRange,
    Row,
    Target,
    YAxes,
    YAxis,
)
from grafanalib.cloudwatch import CloudwatchMetricsTarget

from lib.commons import (
    ALERT_THRESHOLD,
    DEFAULT_REFRESH,
    EDITABLE,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)

from lib.templating import get_release_templating
from lib.lambdas import (
    lambda_generate_invocations_graph,
    lambda_generate_duration_graph,
    lambda_generate_memory_utilization_percentage_graph,
    lambda_generate_memory_utilization_graph,
    lambda_generate_logs_panel,
)
from lib import colors

from typing import List

# https://docs.aws.amazon.com/step-functions/latest/dg/procedure-cw-metrics.html

NAMESPACE = "AWS/States"
SFN_DASHBOARD_PREFIX = "Step Function: "

DURATION_MINIMUM_ALIAS = "Min"
DURATION_AVERAGE_ALIAS = "Avg"
DURATION_MAXIMUM_ALIAS = "Max"

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


def generate_sfn_execution_metrics_graph(
    name: str, cloudwatch_data_source: str, notifications: List[str], *args, **kwargs
):
    """
    Generate step function graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_STARTED_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionsStarted",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_SUCCEEDED_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionsSucceeded",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_ABORTED_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionsAborted",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
            refId=SFN_EXECUTIONS_ABORTED_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_FAILED_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionsFailed",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
            refId=SFN_EXECUTIONS_FAILED_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_THROTTLED_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionsThrottled",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
            refId=SFN_EXECUTIONS_THROTTLED_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=SFN_EXECUTIONS_TIMEDOUT_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionsTimedOut",
            statistics=["Sum"],
            dimensions={"StateMachineArn": name},
            refId=SFN_EXECUTIONS_TIMEDOUT_REF_ID,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT, decimals=2),
        YAxis(format=SHORT_FORMAT, decimals=2),
    )

    seriesOverrides = [
        {
            "alias": SFN_EXECUTIONS_STARTED_ALIAS,
            "points": False,
            "color": colors.BLUE,
        },
        {
            "alias": SFN_EXECUTIONS_SUCCEEDED_ALIAS,
            "points": False,
            "color": colors.GREEN,
        },
        {
            "alias": SFN_EXECUTIONS_ABORTED_ALIAS,
            "points": False,
            "color": colors.RED,
        },
        {
            "alias": SFN_EXECUTIONS_FAILED_ALIAS,
            "points": False,
            "color": colors.RED,
        },
        {
            "alias": SFN_EXECUTIONS_THROTTLED_ALIAS,
            "points": False,
            "color": colors.ORANGE,
        },
        {
            "alias": SFN_EXECUTIONS_TIMEDOUT_ALIAS,
            "points": False,
            "color": colors.RED,
        },
    ]

    alert = None

    # https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
    if notifications:
        alert = Alert(
            name="{} execution issues".format(name),
            message="{} might have failed, aborted, throttled or timedout".format(name),
            executionErrorState="alerting",
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


def generate_sfn_execution_duration_graph(
    name: str, cloudwatch_data_source: str, *args, **kwargs
):
    """
    Generate step function graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias=DURATION_MINIMUM_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionTime",
            statistics=["Minimum"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=DURATION_AVERAGE_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionTime",
            statistics=["Average"],
            dimensions={"StateMachineArn": name},
        ),
        CloudwatchMetricsTarget(
            alias=DURATION_MAXIMUM_ALIAS,
            namespace=NAMESPACE,
            metricName="ExecutionTime",
            statistics=["Maximum"],
            dimensions={"StateMachineArn": name},
        ),
    ]

    yAxes = YAxes(
        YAxis(format=MILLISECONDS_FORMAT, decimals=2),
        YAxis(format=MILLISECONDS_FORMAT, decimals=2),
    )

    seriesOverrides = [
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

    return Graph(
        title="Step function execution duration",
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
    lambda_insights_namespace: str,
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

    sfn_execution_duration_graph = generate_sfn_execution_duration_graph(
        name=name,
        cloudwatch_data_source=cloudwatch_data_source,
    )

    sfn_execution_metrics_graph = generate_sfn_execution_metrics_graph(
        name=name,
        cloudwatch_data_source=cloudwatch_data_source,
        notifications=notifications,
    )

    rows = [
        Row(
            title="Step Function Execution Metrics",
            showTitle=True,
            panels=[sfn_execution_duration_graph, sfn_execution_metrics_graph],
        )
    ]

    if lambdas:
        tags = tags + ["lambda"]

        for l in lambdas:
            lambda_metrics_row = Row(
                title="{} Lambda Metrics".format(l),
                showTitle=True,
                collapse=False,
                panels=[
                    lambda_generate_invocations_graph(
                        l, cloudwatch_data_source, notifications=[]
                    ),
                    lambda_generate_duration_graph(l, cloudwatch_data_source),
                    lambda_generate_memory_utilization_percentage_graph(
                        l,
                        cloudwatch_data_source,
                        lambda_insights_namespace,
                        notifications=notifications,
                    ),
                    lambda_generate_memory_utilization_graph(
                        l, cloudwatch_data_source, lambda_insights_namespace
                    ),
                ],
            )
            lambda_logs_row = Row(
                title="{} Lambda Logs".format(l),
                showTitle=True,
                collapse=True,
                panels=[
                    lambda_generate_logs_panel(l, cloudwatch_data_source),
                ],
            )

            rows.append(lambda_metrics_row)
            rows.append(lambda_logs_row)

    return Dashboard(
        title="{}{}".format(SFN_DASHBOARD_PREFIX, sfn_name),
        editable=EDITABLE,
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
        refresh=DEFAULT_REFRESH,
    ).auto_panel_ids()
