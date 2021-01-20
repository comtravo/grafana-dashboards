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
from grafanalib.cloudwatch import CloudwatchMetricsTarget

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

NAMESPACE = "AWS/RDS"


def generate_rds_cpu_graph(
    name: str, cloudwatch_data_source: str, notifications: List[str]
):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)
    min_alias = "min"
    max_alias = "max"
    mean_alias = "mean"

    targets = [
        CloudwatchMetricsTarget(
            alias=max_alias,
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
            statistics=["Maximum"],
            metricName="CPUUtilization",
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=mean_alias,
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            statistics=["Average"],
            metricName="CPUUtilization",
            period="1m",
        ),
        CloudwatchMetricsTarget(
            alias=min_alias,
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            statistics=["Minimum"],
            metricName="CPUUtilization",
            period="1m",
        ),
    ]

    series_overrides = get_series_overrides(min_alias, mean_alias, max_alias)

    alert = None

    if notifications:
        alert = Alert(
            name="{} CPU utilization Errors".format(name),
            message="{} is having CPU utilization errors".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(80),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="2m",
            frequency="2m",
            notifications=notifications,
        )

    return Graph(
        title="CPU utilization",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
        alert=alert,
    ).auto_ref_ids()


def generate_rds_database_connections_graph(name: str, cloudwatch_data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT)
    min_alias = "min"
    max_alias = "max"
    mean_alias = "mean"

    targets = [
        CloudwatchMetricsTarget(
            alias=max_alias,
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            metricName="DatabaseConnections",
            statistics=["Maximum"],
            period="1m",
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=mean_alias,
            metricName="DatabaseConnections",
            statistics=["Average"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
        CloudwatchMetricsTarget(
            alias=min_alias,
            metricName="DatabaseConnections",
            statistics=["Minimum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
    ]

    series_overrides = get_series_overrides(min_alias, mean_alias, max_alias)

    return Graph(
        title="Database connections",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_burst_balance_graph(
    name: str, cloudwatch_data_source: str, notifications: List[str]
):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)

    targets = [
        CloudwatchMetricsTarget(
            alias="Burst balance",
            metricName="BurstBalance",
            statistics=["Minimum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None

    if notifications:
        alert = Alert(
            name="{} Burst Balance Errors".format(name),
            message="{} is having Burst Balance errors".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=LowerThan(40),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="2m",
            frequency="2m",
            notifications=notifications,
        )

    return Graph(
        title="Burst Balance",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
        alert=alert,
    ).auto_ref_ids()


def generate_rds_transaction_id_graph(
    name: str, cloudwatch_data_source: str, notifications: List[str]
):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT)

    targets = [
        CloudwatchMetricsTarget(
            alias="Transaction ids used",
            metricName="MaximumUsedTransactionIDs",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None

    if notifications:
        alert = Alert(
            name="{} transaction ids used Errors".format(name),
            message="{} is having transaction ids used errors".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=GreaterThan(1000000000),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="2m",
            frequency="2m",
            notifications=notifications,
        )

    return Graph(
        title="Transaction ids used",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
        alert=alert,
    ).auto_ref_ids()


def generate_rds_freeable_memory_graph(name: str, cloudwatch_data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=BYTES)

    targets = [
        CloudwatchMetricsTarget(
            alias="Freeable memory",
            metricName="FreeableMemory",
            statistics=["Minimum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias="Swap memory",
            metricName="SwapUsage",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
    ]

    return Graph(
        title="Memory",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_free_storage_space_graph(name: str, cloudwatch_data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=BYTES)

    targets = [
        CloudwatchMetricsTarget(
            alias="Free storage",
            metricName="FreeStorageSpace",
            statistics=["Minimum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
            refId=ALERT_REF_ID,
        ),
    ]

    return Graph(
        title="Free storage",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_disk_latency_graph(name: str, cloudwatch_data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=SECONDS)

    targets = [
        CloudwatchMetricsTarget(
            alias="read latency",
            metricName="ReadLatency",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
        CloudwatchMetricsTarget(
            alias="write latency",
            metricName="WriteLatency",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
    ]

    return Graph(
        title="Disk latency",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_disk_ops_graph(name: str, cloudwatch_data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT, min=None)

    targets = [
        CloudwatchMetricsTarget(
            alias="write iops",
            metricName="WriteIOPS",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
        CloudwatchMetricsTarget(
            alias="read iops",
            metricName="ReadIOPS",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
        CloudwatchMetricsTarget(
            alias="disk queue depth",
            metricName="DiskQueueDepth",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
    ]

    return Graph(
        title="Disk iops",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=False,
        lines=True,
    ).auto_ref_ids()


def generate_rds_network_throughput_graph(name: str, cloudwatch_data_source: str):
    """
    Generate rds graph
    """

    y_axes = single_y_axis(format=BYTES_SEC, min=None)

    targets = [
        CloudwatchMetricsTarget(
            alias="RX",
            metricName="NetworkReceiveThroughput",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
        ),
        CloudwatchMetricsTarget(
            alias="TX",
            metricName="NetworkTransmitThroughput",
            statistics=["Maximum"],
            namespace=NAMESPACE,
            dimensions={"DBInstanceIdentifier": name},
            period="1m",
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
        dataSource=cloudwatch_data_source,
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
    influxdb_data_source: str,
    cloudwatch_data_source: str,
    engine: str,
    notifications: List[str],
    **kwargs
):

    tags = [environment, engine, "rds", "database"]

    cpu_graph = generate_rds_cpu_graph(
        name=name,
        cloudwatch_data_source=cloudwatch_data_source,
        notifications=notifications,
    )
    burst_graph = generate_rds_burst_balance_graph(
        name=name,
        cloudwatch_data_source=cloudwatch_data_source,
        notifications=notifications,
    )
    connections_graph = generate_rds_database_connections_graph(
        name=name, cloudwatch_data_source=cloudwatch_data_source
    )
    freeable_memory_graph = generate_rds_freeable_memory_graph(
        name=name, cloudwatch_data_source=cloudwatch_data_source
    )
    free_storage_graph = generate_rds_free_storage_space_graph(
        name=name, cloudwatch_data_source=cloudwatch_data_source
    )

    rows = [
        Row(panels=[cpu_graph, burst_graph]),
        Row(panels=[connections_graph, freeable_memory_graph, free_storage_graph]),
        Row(
            panels=[
                generate_rds_disk_latency_graph(
                    name=name, cloudwatch_data_source=cloudwatch_data_source
                ),
                generate_rds_disk_ops_graph(
                    name=name, cloudwatch_data_source=cloudwatch_data_source
                ),
                generate_rds_network_throughput_graph(
                    name=name, cloudwatch_data_source=cloudwatch_data_source
                ),
            ]
        ),
    ]

    if engine == "postgres":
        rows += [
            Row(
                panels=[
                    generate_rds_transaction_id_graph(
                        name=name,
                        cloudwatch_data_source=cloudwatch_data_source,
                        notifications=notifications,
                    )
                ]
            )
        ]

    return Dashboard(
        title="RDS: {}".format(name),
        editable=EDITABLE,
        annotations=get_release_annotations(influxdb_data_source),
        templating=get_release_templating(influxdb_data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
        links=[
            get_documentation_link(
                "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/MonitoringOverview.html"
            )
        ],
    ).auto_panel_ids()
