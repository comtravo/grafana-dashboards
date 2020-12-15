"""
    https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MonitoringOverview.html
"""

from typing import List
from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    LowerThan,
    # MILLISECONDS_FORMAT,
    OP_AND,
    PERCENT_FORMAT,
    RTYPE_MAX,
    single_y_axis,
    # SHORT_FORMAT,
    TimeRange,
    Row,
    Target,
    YAxes,
    YAxis,
)
from grafanalib.influxdb import InfluxDBTarget

from lib import colors
from lib.annotations import get_release_annotations
from lib.commons import (
    ALERT_REF_ID,
    EDITABLE,
    get_documentation_link,
    get_series_overrides,
    RAW_QUERY,
    RETENTION_POLICY,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)
from lib.templating import get_release_templating

RDS_MEASUREMENT = "cloudwatch_aws_rds"


def generate_rds_cpu_graph(name: str, data_source: str, notifications: List[str]):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)
    min_alias = "min"
    max_alias = "max"
    mean_alias = "mean"

    targets = [
        InfluxDBTarget(
            alias=max_alias,
            query='SELECT max("cpu_utilization_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID,
        ),
        InfluxDBTarget(
            alias=mean_alias,
            query='SELECT mean("cpu_utilization_average") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=min_alias,
            query='SELECT min("cpu_utilization_minimum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    series_overrides = get_series_overrides(min_alias, mean_alias, max_alias)

    alert = None

    if notifications:
        alert = Alert(
            name="{} CPU utilization Errors".format(name),
            message="{} is having CPU utilization errors".format(name),
            executionErrorState="alerting",
            noDataState="keep_state",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(80),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="CPU utilization",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
        alert=alert,
    ).auto_ref_ids()


def generate_rds_burst_balance_graph(
    name: str, data_source: str, notifications: List[str]
):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)

    targets = [
        InfluxDBTarget(
            query='SELECT min("burst_balance_minimum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None

    if notifications:
        alert = Alert(
            name="{} Burst Balance Errors".format(name),
            message="{} is having Burst Balance errors".format(name),
            executionErrorState="alerting",
            noDataState="keep_state",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=LowerThan(40),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Burst Balance",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
        alert=alert,
    ).auto_ref_ids()


def generate_rds_dashboard(
    name: str,
    environment: str,
    data_source: str,
    engine: str,
    notifications: List[str],
    **kwargs
):

    tags = [environment, engine, "rds", "database"]

    cpu_graph = generate_rds_cpu_graph(
        name=name, data_source=data_source, notifications=notifications
    )
    burst_graph = generate_rds_burst_balance_graph(
        name=name, data_source=data_source, notifications=notifications
    )

    return Dashboard(
        title="RDS: {}".format(name),
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_templating(data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[Row(panels=[cpu_graph, burst_graph])],
        links=[
            get_documentation_link(
                "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MonitoringOverview.html"
            )
        ],
    ).auto_panel_ids()
