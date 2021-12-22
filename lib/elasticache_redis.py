"""
    https://aws.amazon.com/blogs/database/monitoring-best-practices-with-amazon-elasticache-for-redis-using-amazon-cloudwatch/
"""

from typing import List

from grafanalib.cloudwatch import CloudwatchMetricsTarget
from grafanalib.core import (
    MILLISECONDS_FORMAT,
    OP_OR,
    PERCENT_FORMAT,
    RTYPE_MAX,
    SHORT_FORMAT,
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    LowerThan,
    Row,
    Target,
    TimeRange,
    YAxes,
    YAxis,
    single_y_axis,
)
from grafanalib.formatunits import BYTES

from lib import colors
from lib.commons import ALERT_REF_ID, EDITABLE, SHARED_CROSSHAIR, TIMEZONE, TRANSPARENT

ELASTICACHE_MEASUREMENT = "cloudwatch_aws_elasticache"
NAMESPACE = "AWS/ElastiCache"

DOCUMENTATION_LINK = {
    "targetBlank": True,
    "title": "Documentation",
    "url": "https://aws.amazon.com/blogs/database/monitoring-best-practices-with-amazon-elasticache-for-redis-using-amazon-cloudwatch/",
}


def generate_elasticache_redis_db_memory_usage_and_evicitons_graph(
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = YAxes(
        YAxis(format=PERCENT_FORMAT),
        YAxis(format=SHORT_FORMAT),
    )
    aliases = {
        "db usage": "Database memory usage percentage",
        "evictions": "Evictions",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["db usage"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="DatabaseMemoryUsagePercentage",
        ),
        CloudwatchMetricsTarget(
            alias=aliases["evictions"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
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
            "alias": aliases["evictions"],
            "color": colors.RED,
            "lines": True,
            "bars": False,
            "yaxis": 2,
        },
    ]

    return Graph(
        title="DB memory usage and Evictions",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_swap_and_memory_usage_graph(
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = single_y_axis(format=BYTES)
    aliases = {
        "bytes": "Bytes used for cache",
        "swap": "Swap Usage",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["bytes"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="BytesUsedForCache",
        ),
        CloudwatchMetricsTarget(
            alias=aliases["swap"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="SwapUsage",
        ),
    ]

    series_overrides = [
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
        },
    ]

    return Graph(
        title="Memory and Swap usage",
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
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)
    aliases = {
        "engine utilization": "Engine CPU utilization",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["engine utilization"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="EngineCPUUtilization",
        ),
    ]

    series_overrides = [
        {
            "alias": aliases["engine utilization"],
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        },
    ]

    return Graph(
        title="Engine CPU utilization",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_cpu_credit_usage_graph(
    cache_cluster_id: str, cloudwatch_data_source: str, notifications: List[str]
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT)
    aliases = {
        "credit balance": "CPU credit balance",
        "credit usage": "CPU credit usage",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["credit balance"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Minimum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="CPUCreditBalance",
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=aliases["credit usage"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="CPUCreditUsage",
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
            "alias": aliases["credit usage"],
            "color": colors.YELLOW,
            "lines": True,
            "bars": False,
        },
    ]

    return Graph(
        title="CPU credit utilization",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
        alert=alert,
    ).auto_ref_ids()


def generate_elasticache_redis_network_in_graph(
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = single_y_axis(format=BYTES)
    aliases = {
        "in": "Network bytes in",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["in"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
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
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = single_y_axis(format=BYTES)
    aliases = {
        "out": "Network bytes out",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["out"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
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


def generate_elasticache_redis_connections_graph(
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = single_y_axis(format=SHORT_FORMAT)
    aliases = {
        "current": "Current connections",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["current"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="CurrConnections",
            refId=ALERT_REF_ID,
        ),
    ]

    series_overrides = [
        {
            "alias": aliases["current"],
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        },
    ]

    return Graph(
        title="Current connections",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_replication_graph(
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = YAxes(
        YAxis(format=BYTES),
        YAxis(format=MILLISECONDS_FORMAT),
    )

    aliases = {
        "bytes": "Replication bytes",
        "lag": "Replication lag",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["bytes"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="ReplicationBytes",
        ),
        CloudwatchMetricsTarget(
            alias=aliases["lag"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="ReplicationLag",
        ),
    ]

    series_overrides = [
        {
            "alias": aliases["bytes"],
            "color": colors.GREEN,
            "lines": False,
            "bars": True,
        },
        {
            "alias": aliases["lag"],
            "color": colors.RED,
            "lines": True,
            "bars": False,
            "yaxis": 2,
        },
    ]

    return Graph(
        title="Replication",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=series_overrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        bars=True,
        lines=False,
    ).auto_ref_ids()


def generate_elasticache_redis_latency_graph(
    cache_cluster_id: str, cloudwatch_data_source: str
) -> Graph:
    """
    Generate ElastiCache Redis graph
    """

    y_axes = single_y_axis(format=MILLISECONDS_FORMAT)

    aliases = {
        "latency": "String based CMDs latency",
    }

    targets = [
        CloudwatchMetricsTarget(
            alias=aliases["latency"],
            namespace=NAMESPACE,
            period="1m",
            statistics=["Maximum"],
            dimensions={"CacheClusterId": cache_cluster_id},
            metricName="StringBasedCmdsLatency",
        ),
    ]

    series_overrides = [
        {
            "alias": aliases["latency"],
            "color": colors.GREEN,
            "lines": True,
            "bars": False,
        },
    ]

    return Graph(
        title="Latency",
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
    cache_cluster_id: str,
    influxdb_data_source: str,
    cloudwatch_data_source: str,
    environment: str,
    notifications: List[str],
    *args,
    **kwargs,
):
    """Generate ElastiCache Redis dashboard"""
    tags = ["elasticache", "redis", environment]

    rows = [
        Row(
            panels=[
                generate_elasticache_redis_cpu_usage_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
                generate_elasticache_redis_cpu_credit_usage_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                    notifications=notifications,
                ),
                generate_elasticache_redis_swap_and_memory_usage_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
            ],
            editable=EDITABLE,
        ),
        Row(
            panels=[
                generate_elasticache_redis_network_in_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
                generate_elasticache_redis_connections_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
                generate_elasticache_redis_db_memory_usage_and_evicitons_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
            ],
            editable=EDITABLE,
        ),
        Row(
            panels=[
                generate_elasticache_redis_network_out_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
                generate_elasticache_redis_replication_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
                generate_elasticache_redis_latency_graph(
                    cache_cluster_id=cache_cluster_id,
                    cloudwatch_data_source=cloudwatch_data_source,
                ),
            ],
            editable=EDITABLE,
        ),
    ]

    return Dashboard(
        title="ElastiCache Redis: {}".format(name),
        editable=EDITABLE,
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        rows=rows,
        links=[DOCUMENTATION_LINK],
    ).auto_panel_ids()
