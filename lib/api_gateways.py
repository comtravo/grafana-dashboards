from typing import List

from grafanalib.cloudwatch import CloudwatchMetricsTarget
from grafanalib.core import (
    OP_AND,
    RTYPE_MAX,
    SHORT_FORMAT,
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    Row,
    Target,
    TimeRange,
    YAxes,
    YAxis,
)

from lib import colors
from lib.commons import (
    ALERT_REF_ID,
    ALERT_THRESHOLD,
    DEFAULT_REFRESH,
    EDITABLE,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)
from lib.lambdas import (
    lambda_generate_duration_graph,
    lambda_generate_invocations_graph,
    lambda_generate_logs_panel,
    lambda_generate_memory_utilization_graph,
    lambda_generate_memory_utilization_percentage_graph,
)

# https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-metrics-and-dimensions.html
API_GATEWAY_INVOCATION_METRIC_GROUP_BY = "1m"
NAMESPACE = "AWS/ApiGateway"
API_GATEWAY_4XX_ALIAS = "4xx"
API_GATEWAY_4XX_REF_ID = "B"
API_GATEWAY_4XX_ALERT_ALIAS = "alert_query"
API_GATEWAY_5XX_ALIAS = "5xx"
API_GATEWAY_REQUESTS_ALIAS = "requests"
API_GATEWAY_REQUESTS_REF_ID = "C"


def generate_api_gateway_requests_graph(
    name: str, cloudwatch_data_source: str, notifications: List[str], *args, **kwargs
):
    targets = [
        CloudwatchMetricsTarget(
            alias=API_GATEWAY_5XX_ALIAS,
            namespace=NAMESPACE,
            statistics=["Sum"],
            metricName="5XXError",
            dimensions={"ApiName": name},
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=API_GATEWAY_REQUESTS_ALIAS,
            namespace=NAMESPACE,
            statistics=["Sum"],
            metricName="Count",
            dimensions={"ApiName": name},
            refId=API_GATEWAY_REQUESTS_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=API_GATEWAY_4XX_ALIAS,
            namespace=NAMESPACE,
            statistics=["Sum"],
            metricName="4XXError",
            dimensions={"ApiName": name},
            refId=API_GATEWAY_4XX_REF_ID,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )

    seriesOverrides = [
        {
            "alias": API_GATEWAY_REQUESTS_ALIAS,
            "points": False,
            "color": colors.GREEN,
        },
        {
            "alias": API_GATEWAY_4XX_ALIAS,
            "color": colors.YELLOW,
        },
        {
            "alias": API_GATEWAY_5XX_ALIAS,
            "color": colors.RED,
        },
    ]

    alert = None

    # https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
    if notifications:
        alert = Alert(
            name="{} API Gateway 5XX Errors".format(name),
            message="{} is having 5XX errors".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            frequency="2m",
            gracePeriod="2m",
            notifications=notifications,
        )

    return Graph(
        title="API Gateway Requests: {}".format(name),
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def generate_api_gateways_dashboard(
    name: str,
    cloudwatch_data_source: str,
    lambda_insights_namespace: str,
    notifications: List[str],
    environment: str,
    lambdas: List[str],
    *args,
    **kwargs,
):
    tags = ["api-gateway", environment]

    if lambdas:
        tags = tags + ["lambda"]

    api_gateway_graph = generate_api_gateway_requests_graph(
        name, cloudwatch_data_source, notifications
    )

    rows = [
        Row(title="API Gateway Metrics", showTitle=True, panels=[api_gateway_graph])
    ]

    if lambdas:
        for lambda_fn in lambdas:
            lambda_metrics_row = Row(
                title="{} Lambda Metrics".format(lambda_fn),
                showTitle=True,
                collapse=False,
                panels=[
                    lambda_generate_invocations_graph(
                        name, cloudwatch_data_source, notifications=[]
                    ),
                    lambda_generate_duration_graph(name, cloudwatch_data_source),
                    lambda_generate_memory_utilization_percentage_graph(
                        name,
                        cloudwatch_data_source,
                        lambda_insights_namespace,
                        notifications=notifications,
                    ),
                    lambda_generate_memory_utilization_graph(
                        name, cloudwatch_data_source, lambda_insights_namespace
                    ),
                ],
            )
            lambda_logs_row = Row(
                title="{} Lambda Logs".format(lambda_fn),
                showTitle=True,
                collapse=True,
                panels=[
                    lambda_generate_logs_panel(name, cloudwatch_data_source),
                ],
            )

            rows.append(lambda_metrics_row)
            rows.append(lambda_logs_row)

    return Dashboard(
        title="{} {}".format("API Gateway:", name),
        editable=EDITABLE,
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        refresh=DEFAULT_REFRESH,
        rows=rows,
    ).auto_panel_ids()
