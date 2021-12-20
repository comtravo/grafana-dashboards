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
    LowerThan,
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

def generate_running_count_stats_panel(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    grid_pos: GridPos,
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
      ],
      gridPos=grid_pos
    )

def generate_cpu_utilization_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    grid_pos: GridPos,
    *args,
    **kwargs
) -> Graph:
    """
    Generate CPU graph
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
        gridPos=grid_pos,
    ).auto_ref_ids()

def generate_mem_utilization_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    memory: str,
    notifications: List[str],
    grid_pos:GridPos,
    *args,
    **kwargs
) -> Graph:
    """
    Generate Mem graph
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
        gridPos=grid_pos,
    ).auto_ref_ids()

def generate_req_count_graph(
    name: str,
    cloudwatch_data_source: str,
    loaadbalancer: str,
    target_group: str,
    grid_pos: GridPos,
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
        gridPos=grid_pos,
    ).auto_ref_ids()


def generate_res_count_graph(
    name: str,
    cloudwatch_data_source: str,
    loaadbalancer: str,
    target_group: str,
    grid_pos: GridPos,
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
        gridPos=grid_pos,
    ).auto_ref_ids()

def generate_deployment_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    grid_pos: GridPos,
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
        tooltipMode="none",
        gridPos=grid_pos,
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

def generate_running_count_graph(name: str, cluster_name: str, max: int, cloudwatch_data_source: str, notifications: List[str], grid_pos: GridPos, *args, **kwargs):
    targets = [
        CloudwatchMetricsTarget(
            alias="Containers",
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

    alert = None
    if notifications:
        alert = Alert(
            name="{} Running count of containers nearing the max".format(name),
            message="{} is having Running count of containers nearing the max".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0.9 * max), # 90% of max
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Running Tasks",
        dataSource=cloudwatch_data_source,
        targets=targets,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        gridPos=grid_pos,
    ).auto_ref_ids()

def generate_desired_count_graph(name: str, cluster_name: str, max: int, cloudwatch_data_source: str, notifications: List[str], grid_pos: GridPos, *args, **kwargs):
    targets = [
        CloudwatchMetricsTarget(
            alias="Containers",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="DesiredTaskCount",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="{} Desired count of containers nearing the max".format(name),
            message="{} is having Desired count of containers nearing the max".format(name),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0.9 * max), # 90% of max
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Desired Tasks",
        dataSource=cloudwatch_data_source,
        targets=targets,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        gridPos=grid_pos,
    ).auto_ref_ids()


def generate_pending_count_graph(name: str, cluster_name: str, cloudwatch_data_source: str, notifications: List[str], grid_pos: GridPos, *args, **kwargs):
    targets = [
        CloudwatchMetricsTarget(
            alias="Containers",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="PendingTaskCount",
            dimensions={
              "ServiceName": name,
              "ClusterName": cluster_name
              },
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="{} Pending count of containers is greater than zero".format(name),
            message="{} is having Pending count of containers is greater than zero".format(name),
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
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Pending Tasks",
        dataSource=cloudwatch_data_source,
        targets=targets,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        gridPos=grid_pos,
    ).auto_ref_ids()


def generate_ecs_alb_service_dashboard(
    name: str,
    cluster_name: str,
    cloudwatch_data_source: str,
    notifications: List[str],
    environment: str,
    *args,
    **kwargs
):
  """Generate ECS Service dashboard
  """
  tags = ["ecs", "ecs-service", "containers", "service", environment]

  panels = [
        RowPanel(
            title="Summary",
            gridPos=GridPos(1, 24, 0, 0),
        ),
        generate_running_count_stats_panel(name=name, cluster_name=cluster_name, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8, 12, 0, 1), notifications=notifications, *args, **kwargs),
        generate_deployment_graph(name=name, cluster_name=cluster_name, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8, 12, 12, 1), *args, **kwargs),
        RowPanel(
            title="Capacity",
            gridPos=GridPos(1, 24, 0, 9)
        ),
        generate_running_count_graph(name=name, cluster_name=cluster_name, max=max, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8,8,0,10), notifications=notifications),
        generate_desired_count_graph(name=name, cluster_name=cluster_name, max=max, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8,8,8,10), notifications=notifications),
        generate_pending_count_graph(name=name, cluster_name=cluster_name, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8,8,16,10), notifications=notifications),
        RowPanel(
            title="Utilization",
            gridPos=GridPos(1, 24, 0, 18)
        ),
        generate_cpu_utilization_graph(name=name, cluster_name=cluster_name, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8,12, 0, 19), *args, **kwargs),
        generate_mem_utilization_graph(name=name, cluster_name=cluster_name, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8,12, 12, 19), notifications=notifications, *args, **kwargs),
        RowPanel(
            title="Requests and Responses",
            gridPos=GridPos(1, 24, 0, 27)
        ),
      generate_req_count_graph(name=name, cluster_name=cluster_name, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8, 12, 0, 28), *args, **kwargs),
      generate_res_count_graph(name=name, cluster_name=cluster_name, cloudwatch_data_source=cloudwatch_data_source, grid_pos=GridPos(8, 12, 12, 28), *args, **kwargs)
    # RowPanel(title="Error logs", panels=[
    #   generate_5xx_logs_panel(name=name, *args, **kwargs),
    # ])
  ]
  return Dashboard(
      title="{} {}".format("ECS Service:", name),
      editable=EDITABLE,
      tags=tags,
      timezone=TIMEZONE,
      sharedCrosshair=SHARED_CROSSHAIR,
      panels=panels,
    #   rows=rows,
  ).auto_panel_ids()
