"""
    https://aws.amazon.com/blogs/database/monitoring-best-practices-with-amazon-elasticache-for-redis-using-amazon-cloudwatch/
"""

from typing import List
from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    LowerThan,
    Graph,
    GreaterThan,
    OP_OR,
    PERCENT_FORMAT,
    Repeat,
    Row,
    RTYPE_MAX,
    SHORT_FORMAT,
    Target,
    Template,
    Templating,
    TimeRange,
    single_y_axis,
    YAxes,
    YAxis,
)
from grafanalib.formatunits import MEGA_BYTES
from grafanalib.cloudwatch import CloudwatchMetricsTarget

from lib.annotations import get_release_annotations
from lib.templating import get_release_templating
from lib import colors
from lib.commons import (
    ALERT_REF_ID,
    EDITABLE,
    RAW_QUERY,
    RETENTION_POLICY,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)

ELASTICACHE_MEASUREMENT = "cloudwatch_aws_es"
NAMESPACE = "AWS/ES"

DOCUMENTATION_LINK = {
    "targetBlank": True,
    "title": "Documentation",
    "url": "https://aws.amazon.com/blogs/database/monitoring-best-practices-with-amazon-elasticache-for-redis-using-amazon-cloudwatch/",
}


def generate_elasticache_redis_memory_usage_graph(
    name: str, client_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    """
    "CurrConnections",
    "NetworkBytesIn",
    "NetworkBytesOut",
    "ReplicationBytes",
    "ReplicationLag",
    "SaveInProgress",
    "StringBasedCmdsLatency",
    """

    y_axes = YAxes(
        YAxis(format=PERCENT_FORMAT),
        YAxis(format=MEGA_BYTES),
    )
    aliases = {
        "bytes": "Bytes used for cache",
        "db usage": "Database memory usage percentage",
        "swap": "SwapUsage",
        "evictions": "Evictions",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["bytes"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="BytesUsedForCache",
        ),
        CloudwatchMetricsTarget(
            alias=aliases["db usage"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="DatabaseMemoryUsagePercentage",
        ),
        CloudwatchMetricsTarget(
            alias=aliases["swap"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="SwapUsage",
        ),
        CloudwatchMetricsTarget(
            alias=aliases["evictions"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="Evictions",
        ),
    ]

    series_overrides = [
        {
            "alias": aliases["db usage"],
            "color": colors.ORANGE,
            "lines": True,
            "bars": False,
        },
        {
            "alias": aliases["swap"],
            "color": colors.BLUE,
            "lines": True,
            "bars": False,
        },
        {
            "alias": aliases["bytes"],
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
            "yaxis": 2,
        },
    ]

    return Graph(
        title="Memory usage",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_cpu_usage_graph(
    name: str, client_id: str, cloudwatch_data_source: str, notifications: List[str]
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = YAxes(
        YAxis(format=SHORT_FORMAT),
        YAxis(format=PERCENT_FORMAT),
    )
    aliases = {
        "credit balance": "CPU credit balance",
        "credit usage": "CPU credit usage",
        "engine utilization": "Engine CPU utilization",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["credit balance"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Minimum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="CPUCreditBalance",
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=aliases["credit usage"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="CPUCreditUsage",
        ),
        CloudwatchMetricsTarget(
            alias=aliases["engine utilization"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="EngineCPUUtilization",
        ),
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="ElastiCache Redis CPU credit balance alert",
            message="ElastiCache Redis CPU credit balance alert",
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("5m", "now"),
                    evaluator=LowerThan(250),
                    reducerType=RTYPE_MAX,
                    operator=OP_OR,
                ),
            ],
            frequency="2m",
            gracePeriod="2m",
            notifications=notifications,
        )

    series_overrides = [
        {
            "alias": aliases["credit balance"],
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        },
        {
            "alias": aliases["cedit usage"],
            "color": colors.YELLOW,
            "lines": False,
            "bars": True,
        },
        {
            "alias": aliases["engine utilization"],
            "color": colors.ORANGE,
            "lines": True,
            "bars": False,
            "yaxis": 2,
        },
    ]

    return Graph(
        title="CPU usage",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_network_in_graph(
    name: str, client_id: str, cloudwatch_data_source: str, notifications: List[str]
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = YAxis(format=MEGA_BYTES)
    aliases = {
        "in": "Network bytes in",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["in"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="NetworkBytesIn",
            refId=ALERT_REF_ID,
        ),
    ]

    series_overrides = [
        {
            "alias": aliases["in"],
            "color": colors.GREEN,
            "lines": False,
            "bars": True,
        },
    ]

    return Graph(
        title="Network in",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_network_out_graph(
    name: str, client_id: str, cloudwatch_data_source: str, notifications: List[str]
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = YAxis(format=MEGA_BYTES)
    aliases = {
        "out": "Network bytes out",
    }

    targets = [
        ),
        CloudwatchMetricsTarget(
            alias=aliases["out"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"DomainName": name, "ClientId": client_id},
            metricName="NetworkBytesOut",
        ),
    ]

    series_overrides = [
        {
            "alias": aliases["out"],
            "color": colors.RED,
            "lines": False,
            "bars": True,
        },
    ]

    return Graph(
        title="Network out",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_dashboard(
    name: str,
    client_id: str,
    influxdb_data_source: str,
    cloudwatch_data_source: str,
    environment: str,
    notifications: List[str],
    *args,
    **kwargs
):
    """Generate ElastiCache Redis dashboard"""
    tags = ["elasticache", "redis", environment]

    rows = [
        Row(
            panels=[
                generate_elasticache_redis_cpu_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
                generate_elasticache_redis_jvm_memory_pressure_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                    notifications=notifications,
                ),
            ],
            editable=EDITABLE,
        ),
        Row(
            panels=[
                generate_elasticache_redis_documents_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                )
            ],
            editable=EDITABLE,
        ),
        Row(
            panels=[
                generate_elasticache_redis_storage_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                    notifications=notifications,
                )
            ],
            editable=EDITABLE,
        ),
        Row(
            panels=[
                generate_elasticache_redis_requests_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                )
            ],
            editable=EDITABLE,
        ),
        Row(
            panels=[
                generate_elasticache_redis_status_red_alert_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                    notifications=notifications,
                ),
                generate_elasticache_redis_nodes_alert_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                    notifications=notifications,
                ),
                generate_elasticache_redis_writes_blocked_alert_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                    notifications=notifications,
                ),
                generate_elasticache_redis_automated_snapshot_failure_alert_graph(
                    name=name,
                    client_id=client_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                    notifications=notifications,
                ),
            ],
            editable=EDITABLE,
        ),
    ]

    return Dashboard(
        title="ElastiCache: {}".format(name),
        editable=EDITABLE,
        annotations=get_release_annotations(influxdb_data_source),
        templating=get_release_templating(influxdb_data_source),
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
        links=[DOCUMENTATION_LINK],
    ).auto_panel_ids()
