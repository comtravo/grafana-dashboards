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

from lib.templating import get_release_template
from lib.lambdas import lambda_generate_graph
from lib import colors

from typing import List

import re

# https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-metrics-and-dimensions.html
API_GATEWAY_INVOCATION_METRIC_GROUP_BY = "1m"
API_GATEWAY_MEASUREMENT = "cloudwatch_aws_lambda"
API_GATEWAY_4XX_ALIAS = "4xx"
API_GATEWAY_4XX_REF_ID = "B"
API_GATEWAY_4XX_ALERTS_REF_ID = "D"
API_GATEWAY_5XX_ALIAS = "5xx"
API_GATEWAY_REQUESTS_ALIAS = "requests"
API_GATEWAY_REQUESTS_REF_ID = "C"


def generate_api_gateway_requests_5xx_graph(
    name: str, data_source: str, notifications: List[str], *args, **kwargs
):
    targets = [
        InfluxDBTarget(
            alias=API_GATEWAY_5XX_ALIAS,
            query='SELECT sum("5xx_error_sum") FROM "{}"."{}" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, API_GATEWAY_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID if notifications else None,
        ),
        InfluxDBTarget(
            alias=API_GATEWAY_REQUESTS_ALIAS,
            query='SELECT sum("count_sum") FROM "{}"."{}" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, API_GATEWAY_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=API_GATEWAY_REQUESTS_REF_ID if notifications else None,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )

    seriesOverrides = [
        {
            "alias": API_GATEWAY_REQUESTS_ALIAS,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.GREEN,
        },
        {
            "alias": API_GATEWAY_5XX_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
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
            noDataState="keep_state",
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
        title="API Gateway Requests and 5XX errors: {}".format(name),
        dataSource=data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=yAxes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def generate_api_gateway_requests_4xx_graph(
    name: str, data_source: str, notification: List[str], *args, **kwargs
):
    targets = [
        InfluxDBTarget(
            alias=API_GATEWAY_4XX_ALIAS,
            query='SELECT sum("4xx_error_sum") FROM "{}"."{}" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, API_GATEWAY_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=API_GATEWAY_4XX_REF_ID if notifications else None,
        ),
        InfluxDBTarget(
            alias=API_GATEWAY_REQUESTS_ALIAS,
            query='SELECT sum("count_sum") FROM "{}"."{}" WHERE ("api_name" = \'{}\') AND $timeFilter GROUP BY time(5m) fill(0)'.format(
                RETENTION_POLICY, API_GATEWAY_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=API_GATEWAY_REQUESTS_REF_ID if notifications else None,
        ),
    ]

    yAxes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )

    seriesOverrides = [
        {
            "alias": API_GATEWAY_REQUESTS_ALIAS,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.GREEN,
        },
        {
            "alias": API_GATEWAY_4XX_ALIAS,
            "yaxis": 2,
            "lines": False,
            "points": False,
            "bars": True,
            "color": colors.RED,
        },
    ]

    alert = None

    # https://docs.aws.amazon.com/lambda/latest/dg/monitoring-metrics.html
    if notifications:
        alert = Alert(
            name="{} API Gateway 4XX Errors".format(name),
            message="{} is having 4XX errors".format(name),
            executionErrorState="alerting",
            noDataState="keep_state",
            alertConditions=[
                AlertCondition(
                    Target(refId=API_GATEWAY_REQUESTS_ALIAS),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(9),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                ),
                AlertCondition(
                    Target(refId=API_GATEWAY_4XX_ALIAS),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0.1),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                ),
            ],
            frequency="2m",
            gracePeriod="2m",
            notifications=notifications,
        )

    return Graph(
        title="API Gateway Requests and 4XX errors: {}".format(name),
        dataSource=data_source,
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
    data_source: str,
    notifications: List[str],
    environment: str,
    lambdas: List[str],
    *args,
    **kwargs
):
    tags = ["api-gateway", environment]

    if lambdas:
        tags = tags + ["lambda"]

    api_gateway_4xx_graph = generate_api_gateway_requests_4xx_graph(
        name, data_source, notifications
    )
    api_gateway_5xx_graph = generate_api_gateway_requests_5xx_graph(
        name, data_source, notifications
    )
    lambda_panels = [
        lambda_generate_graph(
            name=l, data_source=data_source, notifications=notifications
        )
        for l in lambdas
    ]

    rows = [Row(panels=[api_gateway_4xx_graph]), Row(panels=[api_gateway_5xx_graph])]

    if lambda_panels:
        rows = rows + [Row(panels=lambda_panels)]

    return Dashboard(
        title="{}{}".format("API Gateway:{}", name),
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_template(data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
    ).auto_panel_ids()
