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
    OP_AND,
    PERCENT_FORMAT,
    RTYPE_MAX,
    single_y_axis,
    SHORT_FORMAT,
    TimeRange,
    Row,
    Target,
    YAxes,
    YAxis,
)
from grafanalib.formatunits import BYTES, BYTES_SEC, SECONDS
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


def generate_rds_database_connections_graph(name: str, data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT)
    min_alias = "min"
    max_alias = "max"
    mean_alias = "mean"

    targets = [
        InfluxDBTarget(
            alias=max_alias,
            query='SELECT max("database_connections_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID,
        ),
        InfluxDBTarget(
            alias=mean_alias,
            query='SELECT mean("database_connections_average") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias=min_alias,
            query='SELECT min("database_connections_minimum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    series_overrides = get_series_overrides(min_alias, mean_alias, max_alias)

    return Graph(
        title="Database connections",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
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
            alias="Burst balance",
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


def generate_rds_freeable_memory_graph(name: str, data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=BYTES)

    targets = [
        InfluxDBTarget(
            alias="Freeable memory",
            query='SELECT min("freeable_memory_minimum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID,
        ),
        InfluxDBTarget(
            alias="Swap memory",
            query='SELECT max("swap_usage_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    return Graph(
        title="Memory",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_free_storage_space_graph(name: str, data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=BYTES)

    targets = [
        InfluxDBTarget(
            alias="Free storage",
            query='SELECT min("free_storage_space_minimum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
            refId=ALERT_REF_ID,
        ),
    ]

    return Graph(
        title="Free storage",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_disk_latency_graph(name: str, data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=SECONDS)

    targets = [
        InfluxDBTarget(
            alias="read latency",
            query='SELECT max("read_latency_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias="write latency",
            query='SELECT max("write_latency_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    return Graph(
        title="Disk latency",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_disk_ops_graph(name: str, data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT, min=None)

    targets = [
        InfluxDBTarget(
            alias="write iops",
            query='SELECT max("write_iops_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias="read iops",
            query='SELECT max("read_iops_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias="disk queue depth",
            query='SELECT max("disk_queue_depth_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    return Graph(
        title="Disk iops",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_network_throughput_graph(name: str, data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=BYTES_SEC, min=None)

    targets = [
        InfluxDBTarget(
            alias="RX",
            query='SELECT max("network_receive_throughput_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
        InfluxDBTarget(
            alias="TX",
            query='SELECT max("network_transmit_throughput_maximum") FROM "{}"."{}" WHERE ("db_instance_identifier" =\'{}\') AND $timeFilter GROUP BY time(1m) fill(previous)'.format(
                RETENTION_POLICY, RDS_MEASUREMENT, name
            ),
            rawQuery=RAW_QUERY,
        ),
    ]

    series_overrides = [
        {
            "alias": "TX",
            "color": colors.GREEN,
            "transform": "negative-Y",
            "fillGradient": 10,
        },
        {"alias": "RX", "color": colors.YELLOW, "fillGradient": 10},
    ]

    return Graph(
        title="Network throughput",
        dataSource=data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
        seriesOverrides=series_overrides,
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
    connections_graph = generate_rds_database_connections_graph(
        name=name, data_source=data_source
    )
    freeable_memory_graph = generate_rds_freeable_memory_graph(
        name=name, data_source=data_source
    )
    free_storage_graph = generate_rds_free_storage_space_graph(
        name=name, data_source=data_source
    )

    return Dashboard(
        title="RDS: {}".format(name),
        editable=EDITABLE,
        annotations=get_release_annotations(data_source),
        templating=get_release_templating(data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=[
            Row(panels=[cpu_graph, burst_graph]),
            Row(panels=[connections_graph, freeable_memory_graph, free_storage_graph]),
            Row(
                panels=[
                    generate_rds_disk_latency_graph(name=name, data_source=data_source),
                    generate_rds_disk_ops_graph(name=name, data_source=data_source),
                    generate_rds_network_throughput_graph(
                        name=name, data_source=data_source
                    ),
                ]
            ),
        ],
        links=[
            get_documentation_link(
                "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MonitoringOverview.html"
            )
        ],
    ).auto_panel_ids()
