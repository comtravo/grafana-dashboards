"""
  https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-metrics.html
"""

from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    GridPos,
    Logs,
    OP_AND,
    Row,
    RowPanel,
    RTYPE_MAX,
    single_y_axis,
    Stat,
    Target,
    TimeRange,
    TimeSeries,
)

from lib.commons import (
    ALERT_REF_ID,
    ALERT_THRESHOLD,
    EDITABLE,
    SHARED_CROSSHAIR,
    TIMEZONE,
    TRANSPARENT,
)

from grafanalib.cloudwatch import CloudwatchMetricsTarget
from grafanalib.elasticsearch import ElasticsearchTarget
from grafanalib.formatunits import MEGA_BYTES, PERCENT_FORMAT
from lib import colors

from typing import List

ECS_NAMESPACE = "AWS/ECS"
CONTAINER_INSIGHTS_NAMESPACE = "ECS/ContainerInsights"

MINIMUM_ALIAS = "Min"
AVERAGE_ALIAS = "Avg"
MAXIMUM_ALIAS = "Max"

def generate_running_count_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    *args,
    **kwargs
) -> Stat:
    """
    Generate lambda graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias="Desired",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="DesiredTaskCount",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
        CloudwatchMetricsTarget(
            alias="Pending",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="PendingTaskCount",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
        CloudwatchMetricsTarget(
            alias="Running",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="RunningTaskCount",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
            refId=ALERT_REF_ID,
        ),
    ]

    return Stat(
        title="Task count",
        dataSource=cloudwatch_data_source,
        targets=targets,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        colorMode="background",
        alignment="center",
        reduceCalc="lastNotNull",
        thresholds=[
        {
          "color": "blue"
        }
      ]
    )

def generate_cpu_utilization_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    *args,
    **kwargs
) -> Graph:
    """
    Generate lambda graph
    """

    y_axes = single_y_axis(format=PERCENT_FORMAT)

    targets = [
        CloudwatchMetricsTarget(
            alias=MINIMUM_ALIAS,
            namespace=ECS_NAMESPACE,
            statistics=["Minimum"],
            metricName="CPUUtilization",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
        CloudwatchMetricsTarget(
            alias=AVERAGE_ALIAS,
            namespace=ECS_NAMESPACE,
            statistics=["Average"],
            metricName="CPUUtilization",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=ECS_NAMESPACE,
            statistics=["Maximum"],
            metricName="CPUUtilization",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
            refId=ALERT_REF_ID,
        ),
    ]

    seriesOverrides = [
        {"alias": MINIMUM_ALIAS, "color": "#C8F2C2", "lines": False},
        {"alias": AVERAGE_ALIAS, "color": "#FADE2A", "fill": 0},
        {
            "alias": MAXIMUM_ALIAS,
            "color": "rgb(77, 159, 179)",
            "fillBelowTo": MINIMUM_ALIAS,
            "lines": False,
        },
    ]

    return Graph(
        title="CPU utilization percentage",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
    ).auto_ref_ids()

def generate_mem_utilization_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    memory: str,
    notifications: List[str],
    *args,
    **kwargs
) -> Graph:
    """
    Generate lambda graph
    """

    y_axes = single_y_axis(format=MEGA_BYTES)
    targets = [
        CloudwatchMetricsTarget(
            alias=MINIMUM_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Minimum"],
            metricName="MemoryUtilized",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
        CloudwatchMetricsTarget(
            alias=AVERAGE_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Average"],
            metricName="MemoryUtilized",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="MemoryUtilized",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
        CloudwatchMetricsTarget(
            alias="Memory reserved",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="MemoryReserved",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
    ]

    seriesOverrides = [
        {"alias": "Memory reserved", "color": colors.RED, "fill": 0},
        {"alias": MINIMUM_ALIAS, "color": "#C8F2C2", "lines": False},
        {"alias": AVERAGE_ALIAS, "color": "#FADE2A", "fill": 0},
        {
            "alias": MAXIMUM_ALIAS,
            "color": "rgb(77, 159, 179)",
            "fillBelowTo": MINIMUM_ALIAS,
            "lines": False,
        },
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="{} Memory utilization Errors".format(name),
            message="{} is having Memory utilization errors".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("30m", "now"),
                    evaluator=GreaterThan(memory),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Memory utilization",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=seriesOverrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
    ).auto_ref_ids()

def generate_req_count_graph(
    name: str,
    cloudwatch_data_source: str,
    loaadbalancer: str,
    target_group: str,
    *args,
    **kwargs
) -> Graph:
    """
    Generate req graph
    """

    request_count_alias = "RequestCount"
    request_count_per_target_alias = "RequestCountPerTarget"

    targets = [
        CloudwatchMetricsTarget(
            alias=request_count_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="RequestCount",
            dimensions={
              "LoadBalancer": loaadbalancer,
              "TargetGroup": target_group
              },
        ),
        CloudwatchMetricsTarget(
            alias=request_count_per_target_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="RequestCountPerTarget",
            dimensions={
              "LoadBalancer": loaadbalancer,
              "TargetGroup": target_group
              },
        ),
    ]

    seriesOverrides = [
        {"alias": request_count_alias, "color": colors.YELLOW, "fill": 0},
        {"alias": request_count_per_target_alias, "color": colors.GREEN, "fill": 0}
    ]

    return Graph(
        title="Requests",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
    ).auto_ref_ids()


def generate_res_count_graph(
    name: str,
    cloudwatch_data_source: str,
    loaadbalancer: str,
    target_group: str,
    *args,
    **kwargs
) -> Graph:
    """
    Generate res graph
    """

    xx2_alias = "2xx"
    xx3_alias = "3xx"
    xx4_alias = "4xx"
    xx5_alias = "5xx"

    targets = [
        CloudwatchMetricsTarget(
            alias=xx2_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="HTTPCode_Target_2XX_Count",
            dimensions={
              "LoadBalancer": loaadbalancer,
              "TargetGroup": target_group
              },
        ),
        CloudwatchMetricsTarget(
            alias=xx3_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="HTTPCode_Target_3XX_Count",
            dimensions={
              "LoadBalancer": loaadbalancer,
              "TargetGroup": target_group
              },
        ),
        CloudwatchMetricsTarget(
            alias=xx4_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="HTTPCode_Target_4XX_Count",
            dimensions={
              "LoadBalancer": loaadbalancer,
              "TargetGroup": target_group
              },
        ),
        CloudwatchMetricsTarget(
            alias=xx5_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="HTTPCode_Target_5XX_Count",
            dimensions={
              "LoadBalancer": loaadbalancer,
              "TargetGroup": target_group
              },
        ),
    ]

    seriesOverrides = [
        {"alias": xx2_alias, "color": colors.GREEN, "fill": 0},
        {"alias": xx3_alias, "color": colors.YELLOW, "fill": 0},
        {"alias": xx4_alias, "color": colors.ORANGE, "fill": 0},
        {"alias": xx5_alias, "color": colors.RED, "fill": 0},
    ]

    return Graph(
        title="Responses",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
    ).auto_ref_ids()

def generate_deployment_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    *args,
    **kwargs
) -> TimeSeries:
    """
    Generate deployment graph
    """

    targets = [
        CloudwatchMetricsTarget(
            alias="Deployment",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="DeploymentCount",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
        ),
    ]

    return TimeSeries(
        title="Deployments",
        dataSource=cloudwatch_data_source,
        targets=targets,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        axisPlacement="hidden",
        tooltipMode="none"
    )


def generate_5xx_logs_panel(name: str, elasticsearch_data_source: str, *args, **kwargs) -> Logs:
    """
    Generate Logs panel
    """
    targets = [
        ElasticsearchTarget(
            query="tag: \"{}\" AND log.res.statusCode: [500 TO *] AND NOT log.msg: \"\"".format(name),
            metricAggs=[
            {
                "id": "1",
                "settings": {
                    "limit": "10000"
                },
                "type": "logs"
            }
          ]
        ),
    ]

    return Logs(
        title="5XX",
        dataSource=elasticsearch_data_source,
        targets=targets,
        wrapLogMessages=False,
        prettifyLogMessage=False,
        enableLogDetails=True,
        dedupStrategy="exact"
    )

def generate_ecs_alb_service_dashboard(
    name: str,
    cloudwatch_data_source: str,
    notifications: List[str],
    environment: str,
    *args,
    **kwargs
):
  """Generate ECS Service dashboard
  """
  tags = ["ecs", "ecs-service", "containers", "service", environment]

  running_count_graph = generate_running_count_graph(name=name, cloudwatch_data_source=cloudwatch_data_source, notifications=notifications, *args, **kwargs)
  deployment_graph = generate_deployment_graph(name=name, cloudwatch_data_source=cloudwatch_data_source, *args, **kwargs)
  rows = [
    Row(title="Deployments",showTitle=True, collapse=False, panels=[
      running_count_graph,
      deployment_graph
    ]),
    Row(title="Utilization",showTitle=True, collapse=False, panels=[
      generate_cpu_utilization_graph(name=name, cloudwatch_data_source=cloudwatch_data_source, *args, **kwargs),
      generate_mem_utilization_graph(name=name, cloudwatch_data_source=cloudwatch_data_source, notifications=notifications, *args, **kwargs)
    ]),
    Row(title="Requests and Responses",showTitle=True, collapse=False, panels=[
      generate_req_count_graph(name=name, cloudwatch_data_source=cloudwatch_data_source, *args, **kwargs),
      generate_res_count_graph(name=name, cloudwatch_data_source=cloudwatch_data_source, *args, **kwargs)
    ]),
    # Row(title="Error logs",showTitle=True, collapse=False, panels=[
    #   generate_5xx_logs_panel(name=name, *args, **kwargs),
    # ])
  ]
  return Dashboard(
      title="{} {}".format("ECS Service:", name),
      editable=EDITABLE,
      tags=tags,
      timezone=TIMEZONE,
      sharedCrosshair=SHARED_CROSSHAIR,
      rows=rows,
  ).auto_panel_ids()
