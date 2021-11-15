"""
  https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-metrics.html
"""

from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    GreaterThan,
    Logs,
    Row,
    Stat,
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
# from lib import colors

from typing import List

ECS_NAMESPACE = "AWS/ECS"
CONTAINER_INSIGHTS_NAMESPACE = "ECS/ContainerInsights"

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

def generate_ecs_service_dashboard(
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
    ])
  ]
  return Dashboard(
      title="{} {}".format("ECS Service:", name),
      editable=EDITABLE,
      tags=tags,
      timezone=TIMEZONE,
      sharedCrosshair=SHARED_CROSSHAIR,
      rows=rows,
  ).auto_panel_ids()
