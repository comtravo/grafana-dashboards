"""
  https://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch-metrics.html
"""

from grafanalib.core import (
    Alert,
    AlertCondition,
    AlertList,
    Dashboard,
    Graph,
    GreaterThan,
    GridPos,
    Logs,
    OP_AND,
    RowPanel,
    RTYPE_MAX,
    single_y_axis,
    Stat,
    Target,
    Text,
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
) -> Stat:
    """
    Generate running count stats panel
    """

    targets = [
        CloudwatchMetricsTarget(
            alias="Desired",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="DesiredTaskCount",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias="Pending",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="PendingTaskCount",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias="Running",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="RunningTaskCount",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
            refId=ALERT_REF_ID,
        ),
    ]

    return Stat(
        title="Task Count",
        dataSource=cloudwatch_data_source,
        targets=targets,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        colorMode="background",
        alignment="center",
        reduceCalc="lastNotNull",
        thresholds=[{"color": "blue"}],
        gridPos=grid_pos,
    )


# def generate_alert_list_panel(name: str, grid_pos: GridPos):
#     return AlertList(
#         title="Alerts: {}".format(name),
#         gridPos=grid_pos,
#         description="Alerts for service {}".format(name),
#         transparent=TRANSPARENT,
#         onlyAlertsOnDashboard=True,
#         show=True
#     )


def generate_cpu_utilization_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    grid_pos: GridPos,
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
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias=AVERAGE_ALIAS,
            namespace=ECS_NAMESPACE,
            statistics=["Average"],
            metricName="CPUUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=ECS_NAMESPACE,
            statistics=["Maximum"],
            metricName="CPUUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
    ]

    seriesOverrides = [
        {"alias": MINIMUM_ALIAS, "color": colors.GREEN, "lines": False},
        {"alias": AVERAGE_ALIAS, "color": colors.YELLOW, "fill": 0},
        {
            "alias": MAXIMUM_ALIAS,
            "color": colors.GREEN,
            "fillBelowTo": MINIMUM_ALIAS,
            "lines": False,
        },
    ]

    return Graph(
        title="CPU Utilization Percentage",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        yAxes=y_axes,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        gridPos=grid_pos,
    )


def generate_mem_utilization_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    grid_pos: GridPos,
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
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias=AVERAGE_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Average"],
            metricName="MemoryUtilized",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="MemoryUtilized",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias="Memory reserved",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="MemoryReserved",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
    ]

    seriesOverrides = [
        {"alias": "Memory reserved", "color": colors.RED, "fill": 0},
        {"alias": MINIMUM_ALIAS, "color": colors.GREEN, "lines": False},
        {"alias": AVERAGE_ALIAS, "color": colors.YELLOW, "fill": 0},
        {
            "alias": MAXIMUM_ALIAS,
            "color": colors.GREEN,
            "fillBelowTo": MINIMUM_ALIAS,
            "lines": False,
        },
    ]

    return Graph(
        title="Memory Utilization",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=seriesOverrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        gridPos=grid_pos,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()

def generate_mem_utilization_percentage_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    notifications: List[str],
    grid_pos: GridPos,
) -> Graph:
    """
    Generate Mem Percentage graph
    """

    y_axes = single_y_axis(format=MEGA_BYTES)
    targets = [
        CloudwatchMetricsTarget(
            alias=MINIMUM_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Minimum"],
            metricName="MemoryUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias=AVERAGE_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Average"],
            metricName="MemoryUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
            refId=ALERT_REF_ID,
        ),
        CloudwatchMetricsTarget(
            alias=MAXIMUM_ALIAS,
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="MemoryUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
    ]

    seriesOverrides = [
        {"alias": MINIMUM_ALIAS, "color": colors.GREEN, "lines": False},
        {"alias": AVERAGE_ALIAS, "color": colors.YELLOW, "fill": 0},
        {
            "alias": MAXIMUM_ALIAS,
            "color": colors.GREEN,
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
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(85),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                )
            ],
            gracePeriod="1m",
            notifications=notifications,
        )

    return Graph(
        title="Memory Utilization Percentage",
        dataSource=cloudwatch_data_source,
        targets=targets,
        yAxes=y_axes,
        seriesOverrides=seriesOverrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        alert=alert,
        gridPos=grid_pos,
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()

def generate_req_count_graph(
    cloudwatch_data_source: str,
    loadbalancer: str,
    target_group: str,
    grid_pos: GridPos,
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
            dimensions={"LoadBalancer": loadbalancer, "TargetGroup": target_group},
        ),
        CloudwatchMetricsTarget(
            alias=request_count_per_target_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="RequestCountPerTarget",
            dimensions={"LoadBalancer": loadbalancer, "TargetGroup": target_group},
        ),
    ]

    seriesOverrides = [
        {"alias": request_count_alias, "color": colors.YELLOW, "fill": 0},
        {"alias": request_count_per_target_alias, "color": colors.GREEN, "fill": 0},
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
    loadbalancer: str,
    target_group: str,
    grid_pos: GridPos,
    notifications: List[str],
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
            dimensions={"LoadBalancer": loadbalancer, "TargetGroup": target_group},
        ),
        CloudwatchMetricsTarget(
            alias=xx3_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="HTTPCode_Target_3XX_Count",
            dimensions={"LoadBalancer": loadbalancer, "TargetGroup": target_group},
        ),
        CloudwatchMetricsTarget(
            alias=xx4_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="HTTPCode_Target_4XX_Count",
            dimensions={"LoadBalancer": loadbalancer, "TargetGroup": target_group},
        ),
        CloudwatchMetricsTarget(
            alias=xx5_alias,
            namespace="AWS/ApplicationELB",
            statistics=["Sum"],
            metricName="HTTPCode_Target_5XX_Count",
            dimensions={"LoadBalancer": loadbalancer, "TargetGroup": target_group},
            refId=ALERT_REF_ID,
        ),
    ]

    seriesOverrides = [
        {"alias": xx2_alias, "color": colors.GREEN, "fill": 0},
        {"alias": xx3_alias, "color": colors.YELLOW, "fill": 0},
        {"alias": xx4_alias, "color": colors.ORANGE, "fill": 0},
        {"alias": xx5_alias, "color": colors.RED, "fill": 0},
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="{} has 5XX errors".format(name),
            message="{} has 5XX errors".format(name),
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
        title="Responses",
        dataSource=cloudwatch_data_source,
        targets=targets,
        seriesOverrides=seriesOverrides,
        transparent=TRANSPARENT,
        editable=EDITABLE,
        gridPos=grid_pos,
        alert=alert,
    )


def generate_deployment_graph(
    name: str,
    cloudwatch_data_source: str,
    cluster_name: str,
    grid_pos: GridPos,
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
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
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


def get_elasticsearch_query(name: str) -> str:
    """
    Get elasticsearch query
    """

    return 'tag: "{}" AND log.level: [50 TO *] AND NOT log.msg: ""'.format(name)


def generate_helpful_resources_panel(
    name: str, grid_pos: GridPos, kibana_url: str
) -> Text:

    content = """
# Helpful resources

## Elasticsearch

<a href="{}" target="_blank">Kibana URL</a>\n
Elasticsearch query to find all error logs: `{}`
    """.format(
        kibana_url, get_elasticsearch_query(name)
    )
    return Text(
        title="Helpful resources",
        transparent=TRANSPARENT,
        content=content,
        mode="markdown",
        gridPos=grid_pos,
    )


def generate_error_logs_panel(
    name: str, elasticsearch_data_source: str, grid_pos: GridPos
) -> Logs:
    """
    Generate Logs panel
    """
    targets = [
        ElasticsearchTarget(
            query=get_elasticsearch_query(name),
            metricAggs=[{"id": "1", "settings": {"limit": "10000"}, "type": "logs"}],
        ),
    ]

    return Logs(
        title="Error Logs",
        dataSource=elasticsearch_data_source,
        targets=targets,
        wrapLogMessages=False,
        prettifyLogMessage=False,
        enableLogDetails=True,
        dedupStrategy="exact",
        gridPos=grid_pos,
        transparent=TRANSPARENT,
    )


def generate_running_count_graph(
    name: str,
    cluster_name: str,
    max: int,
    cloudwatch_data_source: str,
    notifications: List[str],
    grid_pos: GridPos,
):
    targets = [
        CloudwatchMetricsTarget(
            alias="Containers",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="RunningTaskCount",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="{} Running count of containers nearing the max".format(name),
            message="{} is having Running count of containers nearing the max".format(
                name
            ),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0.9 * max),  # 90% of max
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
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def generate_desired_count_graph(
    name: str,
    cluster_name: str,
    max: int,
    cloudwatch_data_source: str,
    notifications: List[str],
    grid_pos: GridPos,
):
    targets = [
        CloudwatchMetricsTarget(
            alias="Containers",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="DesiredTaskCount",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="{} Desired count of containers nearing the max".format(name),
            message="{} is having Desired count of containers nearing the max".format(
                name
            ),
            executionErrorState="alerting",
            alertConditions=[
                AlertCondition(
                    Target(refId=ALERT_REF_ID),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0.9 * max),  # 90% of max
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
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def generate_pending_count_graph(
    name: str,
    cluster_name: str,
    cloudwatch_data_source: str,
    notifications: List[str],
    grid_pos: GridPos,
):
    targets = [
        CloudwatchMetricsTarget(
            alias="Containers",
            namespace=CONTAINER_INSIGHTS_NAMESPACE,
            statistics=["Maximum"],
            metricName="PendingTaskCount",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
            refId=ALERT_REF_ID,
        ),
    ]

    alert = None
    if notifications:
        alert = Alert(
            name="Unable to schedule containers for {}".format(name),
            message="Unable to schedule containers for {}".format(name),
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
        alertThreshold=ALERT_THRESHOLD,
    ).auto_ref_ids()


def generate_ecs_alb_service_dashboard(
    name: str,
    cluster_name: str,
    cloudwatch_data_source: str,
    notifications: List[str],
    environment: str,
    loadbalancer: str,
    target_group: str,
    elasticsearch_data_source: str,
    kibana_url: str,
    max: int,
    *args,
    **kwargs
):
    """Generate ECS Service dashboard"""
    tags = ["ecs", "ecs-service", "containers", "service", environment]

    panels = [
        RowPanel(
            title="Summary",
            gridPos=GridPos(1, 24, 0, 0),
        ),
        generate_running_count_stats_panel(
            name=name,
            cluster_name=cluster_name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 12, 0, 1),
        ),
        generate_deployment_graph(
            name=name,
            cluster_name=cluster_name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 12, 12, 1),
        ),
        # generate_alert_list_panel(
        #     name=name,
        #     grid_pos=GridPos(8, 8, 16, 1),
        # ),
        RowPanel(title="Capacity", gridPos=GridPos(1, 24, 0, 9)),
        generate_running_count_graph(
            name=name,
            cluster_name=cluster_name,
            max=max,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 8, 0, 10),
            notifications=notifications,
        ),
        generate_desired_count_graph(
            name=name,
            cluster_name=cluster_name,
            max=max,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 8, 8, 10),
            notifications=notifications,
        ),
        generate_pending_count_graph(
            name=name,
            cluster_name=cluster_name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 8, 16, 10),
            notifications=notifications,
        ),
        RowPanel(title="Utilization", gridPos=GridPos(1, 24, 0, 18)),
        generate_cpu_utilization_graph(
            name=name,
            cluster_name=cluster_name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 8, 0, 19),
        ),
        generate_mem_utilization_graph(
            name=name,
            cluster_name=cluster_name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 8, 8, 19),
        ),
        generate_mem_utilization_percentage_graph(
            name=name,
            cluster_name=cluster_name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 8, 16, 19),
            notifications=notifications,
        ),
        RowPanel(title="Requests and Responses", gridPos=GridPos(1, 24, 0, 27)),
        generate_req_count_graph(
            loadbalancer=loadbalancer,
            target_group=target_group,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 12, 0, 28),
        ),
        generate_res_count_graph(
            name=name,
            loadbalancer=loadbalancer,
            target_group=target_group,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=GridPos(8, 12, 12, 28),
            notifications=notifications,
        ),
        RowPanel(title="Logs", gridPos=GridPos(1, 24, 0, 36)),
        generate_helpful_resources_panel(
            name=name, grid_pos=GridPos(8, 24, 0, 37), kibana_url=kibana_url
        ),
        generate_error_logs_panel(
            name=name,
            grid_pos=GridPos(24, 24, 0, 45),
            elasticsearch_data_source=elasticsearch_data_source,
        ),
    ]
    return Dashboard(
        title="{} {}".format("ECS Service:", name),
        editable=EDITABLE,
        tags=tags,
        timezone=TIMEZONE,
        sharedCrosshair=SHARED_CROSSHAIR,
        panels=panels,
    ).auto_panel_ids()
