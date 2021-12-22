from grafanalib.core import (
    Alert,
    AlertCondition,
    # Dashboard,
    Graph,
    GreaterThan,
    GridPos,
    # Logs,
    OP_AND,
    # OP_OR,
    # RowPanel,
    RTYPE_MAX,
    # single_y_axis,
    Stat,
    Target,
    # Text,
    TimeRange,
    TimeSeries,
)

from grafanalib.cloudwatch import CloudwatchMetricsTarget

from lib.ecs import (
    generate_running_count_stats_panel,
    generate_deployment_graph,
    generate_cpu_utilization_graph,
    generate_mem_utilization_graph,
    generate_req_count_graph,
)


class TestECSDashboards:
    def test_should_generate_running_count_stats_panel(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)

        expected_targets = [
          CloudwatchMetricsTarget(
              alias="Desired",
              namespace="ECS/ContainerInsights",
              statistics=["Maximum"],
              metricName="DesiredTaskCount",
              dimensions={"ServiceName": name, "ClusterName": cluster_name},
          ),
          CloudwatchMetricsTarget(
              alias="Pending",
              namespace="ECS/ContainerInsights",
              statistics=["Maximum"],
              metricName="PendingTaskCount",
              dimensions={"ServiceName": name, "ClusterName": cluster_name},
          ),
          CloudwatchMetricsTarget(
              alias="Running",
              namespace="ECS/ContainerInsights",
              statistics=["Maximum"],
              metricName="RunningTaskCount",
              dimensions={"ServiceName": name, "ClusterName": cluster_name},
              refId="A",
          ),
        ]

        panel = generate_running_count_stats_panel(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
        )
        panel.should.be.a(Stat)
        panel.title.should.eql("Task Count")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.gridPos.should.eql(grid_pos)
        panel.colorMode.should.eql("background")
        panel.alignment.should.eql("center")
        panel.targets.should.have.length_of(3)
        panel.targets.should.eql(expected_targets)

    def test_should_generate_deployment_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        panel = generate_deployment_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
        )

        panel.should.be.a(TimeSeries)
        panel.title.should.eql("Deployments")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(1)
        panel.targets[0].should.eql(CloudwatchMetricsTarget(
            alias="Deployment",
            namespace="ECS/ContainerInsights",
            statistics=["Maximum"],
            metricName="DeploymentCount",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ))
        panel.gridPos.should.eql(grid_pos)


    def test_should_generate_cpu_utilization_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        panel = generate_cpu_utilization_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
        )

        expected_targets = [
        CloudwatchMetricsTarget(
            alias="Min",
            namespace="AWS/ECS",
            statistics=["Minimum"],
            metricName="CPUUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias="Avg",
            namespace="AWS/ECS",
            statistics=["Average"],
            metricName="CPUUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
        CloudwatchMetricsTarget(
            alias="Max",
            namespace="AWS/ECS",
            statistics=["Maximum"],
            metricName="CPUUtilization",
            dimensions={"ServiceName": name, "ClusterName": cluster_name},
        ),
    ]
        panel.should.be.a(Graph)
        panel.title.should.eql("CPU Utilization Percentage")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(3)
        panel.targets.should.eql(expected_targets)
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_mem_utilization_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        memory = 1024
        notifications=[]

        panel = generate_mem_utilization_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            memory=memory,
            notifications=notifications,
        )
        panel.should.be.a(Graph)
        panel.title.should.eql("Memory Utilization")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(4)
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_mem_utilization_with_alerts_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        memory = 1024
        notifications=["foo", "bar", "baz"]

        expected_alert_condition = AlertCondition(
          Target(refId="A"),
          timeRange=TimeRange("15m", "now"),
          evaluator=GreaterThan(memory),
          reducerType=RTYPE_MAX,
          operator=OP_AND,
        )

        panel = generate_mem_utilization_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            memory=memory,
            notifications=notifications,
        )

        panel.alert.should.be.a(Alert)
        panel.alert.alertConditions.should.have.length_of(1)
        panel.alert.alertConditions[0].should.eql(expected_alert_condition)
        panel.alert.notifications.should.eql(notifications)

    def test_should_generate_req_count_graph(self):
        cloudwatch_data_source = "prod"
        loadbalancer = "loadbalancer-1"
        target_group = "target-group-1"
        grid_pos = GridPos(1, 2, 3, 4)

        panel = generate_req_count_graph(
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=grid_pos,
            loadbalancer=loadbalancer,
            target_group=target_group,
        )
        panel.should.be.a(Graph)
        panel.title.should.eql("Requests")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(2)
