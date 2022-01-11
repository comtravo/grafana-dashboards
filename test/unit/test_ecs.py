from os import name
from grafanalib.core import (
    Alert,
    AlertCondition,
    Dashboard,
    Graph,
    GreaterThan,
    GridPos,
    Logs,
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
from grafanalib.elasticsearch import ElasticsearchTarget

from lib.ecs import (
    generate_running_count_stats_panel,
    generate_deployment_graph,
    generate_running_count_graph,
    generate_desired_count_graph,
    generate_pending_count_graph,
    generate_cpu_utilization_graph,
    generate_mem_utilization_graph,
    generate_mem_utilization_percentage_graph,
    generate_req_count_graph,
    generate_res_count_graph,
    generate_error_logs_panel,
    generate_ecs_alb_service_dashboard,
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
        panel.targets[0].should.eql(
            CloudwatchMetricsTarget(
                alias="Deployment",
                namespace="ECS/ContainerInsights",
                statistics=["Maximum"],
                metricName="DeploymentCount",
                dimensions={"ServiceName": name, "ClusterName": cluster_name},
            )
        )
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_running_count_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        max = 1000
        notifications = []

        panel = generate_running_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            max=max,
            notifications=notifications,
        )

        panel.should.be.a(Graph)
        panel.title.should.eql("Running Tasks")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(1)
        panel.targets[0].should.eql(
            CloudwatchMetricsTarget(
                alias="Containers",
                namespace="ECS/ContainerInsights",
                statistics=["Maximum"],
                metricName="RunningTaskCount",
                dimensions={"ServiceName": name, "ClusterName": cluster_name},
                refId="A",
            )
        )
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_running_count_with_alerts_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        max = 1000
        notifications = ["foo", "bar"]

        panel = generate_running_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            max=max,
            notifications=notifications,
        )

        panel.alert.should.be.a(Alert)
        panel.alert.alertConditions.should.have.length_of(1)
        panel.alert.alertConditions[0].should.eql(
            AlertCondition(
                Target(refId="A"),
                timeRange=TimeRange("15m", "now"),
                evaluator=GreaterThan(900),
                reducerType=RTYPE_MAX,
                operator=OP_AND,
            )
        )

    def test_should_generate_desired_count_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        max = 1000
        notifications = []

        panel = generate_desired_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            max=max,
            notifications=notifications,
        )

        panel.should.be.a(Graph)
        panel.title.should.eql("Desired Tasks")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(1)
        panel.targets[0].should.eql(
            CloudwatchMetricsTarget(
                alias="Containers",
                namespace="ECS/ContainerInsights",
                statistics=["Maximum"],
                metricName="DesiredTaskCount",
                dimensions={"ServiceName": name, "ClusterName": cluster_name},
                refId="A",
            )
        )
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_desired_count_with_alerts_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        max = 1000
        notifications = ["foo", "bar"]

        panel = generate_desired_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            max=max,
            notifications=notifications,
        )

        panel.alert.should.be.a(Alert)
        panel.alert.alertConditions.should.have.length_of(1)
        panel.alert.alertConditions[0].should.eql(
            AlertCondition(
                Target(refId="A"),
                timeRange=TimeRange("15m", "now"),
                evaluator=GreaterThan(900),
                reducerType=RTYPE_MAX,
                operator=OP_AND,
            )
        )

    def test_should_generate_pending_count_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        notifications = []

        panel = generate_pending_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            notifications=notifications,
        )

        panel.should.be.a(Graph)
        panel.title.should.eql("Pending Tasks")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(1)
        panel.targets[0].should.eql(
            CloudwatchMetricsTarget(
                alias="Containers",
                namespace="ECS/ContainerInsights",
                statistics=["Maximum"],
                metricName="PendingTaskCount",
                dimensions={"ServiceName": name, "ClusterName": cluster_name},
                refId="A",
            )
        )
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_pending_count_with_alerts_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        notifications = ["foo", "bar"]

        panel = generate_pending_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            notifications=notifications,
        )

        panel.alert.should.be.a(Alert)
        panel.alert.alertConditions.should.have.length_of(1)
        panel.alert.alertConditions[0].should.eql(
            AlertCondition(
                Target(refId="A"),
                timeRange=TimeRange("15m", "now"),
                evaluator=GreaterThan(0),
                reducerType=RTYPE_MAX,
                operator=OP_AND,
            )
        )

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

        panel = generate_mem_utilization_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
        )
        panel.should.be.a(Graph)
        panel.title.should.eql("Memory Utilization")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(3)
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_mem_utilization_percentage_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        notifications = []

        panel = generate_mem_utilization_percentage_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
            notifications=notifications,
        )
        panel.should.be.a(Graph)
        panel.title.should.eql("Memory Utilization Percentage")
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(3)
        panel.gridPos.should.eql(grid_pos)

    def test_should_generate_mem_utilization_percentage_with_alerts_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        cluster_name = "cluster-1"
        grid_pos = GridPos(1, 2, 3, 4)
        notifications = ["foo", "bar", "baz"]

        expected_alert_condition = AlertCondition(
            Target(refId="A"),
            timeRange=TimeRange("15m", "now"),
            evaluator=GreaterThan(85),
            reducerType=RTYPE_MAX,
            operator=OP_AND,
        )

        panel = generate_mem_utilization_percentage_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            cluster_name=cluster_name,
            grid_pos=grid_pos,
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

    def test_should_generate_res_count_graph(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        loadbalancer = "loadbalancer-1"
        target_group = "target-group-1"
        grid_pos = GridPos(1, 2, 3, 4)
        notifications = []

        panel = generate_res_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=grid_pos,
            loadbalancer=loadbalancer,
            target_group=target_group,
            notifications=notifications,
        )
        panel.should.be.a(Graph)
        panel.title.should.eql("Responses")
        panel.gridPos.should.eql(grid_pos)
        panel.dataSource.should.eql(cloudwatch_data_source)
        panel.targets.should.have.length_of(4)
        panel.targets.should.eql(
            [
                CloudwatchMetricsTarget(
                    alias="2xx",
                    namespace="AWS/ApplicationELB",
                    statistics=["Sum"],
                    metricName="HTTPCode_Target_2XX_Count",
                    dimensions={
                        "LoadBalancer": loadbalancer,
                        "TargetGroup": target_group,
                    },
                ),
                CloudwatchMetricsTarget(
                    alias="3xx",
                    namespace="AWS/ApplicationELB",
                    statistics=["Sum"],
                    metricName="HTTPCode_Target_3XX_Count",
                    dimensions={
                        "LoadBalancer": loadbalancer,
                        "TargetGroup": target_group,
                    },
                ),
                CloudwatchMetricsTarget(
                    alias="4xx",
                    namespace="AWS/ApplicationELB",
                    statistics=["Sum"],
                    metricName="HTTPCode_Target_4XX_Count",
                    dimensions={
                        "LoadBalancer": loadbalancer,
                        "TargetGroup": target_group,
                    },
                ),
                CloudwatchMetricsTarget(
                    alias="5xx",
                    namespace="AWS/ApplicationELB",
                    statistics=["Sum"],
                    metricName="HTTPCode_Target_5XX_Count",
                    dimensions={
                        "LoadBalancer": loadbalancer,
                        "TargetGroup": target_group,
                    },
                    refId="A",
                ),
            ]
        )

    def test_should_generate_res_count_graph_with_alert(self):
        name = "service-1"
        cloudwatch_data_source = "prod"
        loadbalancer = "loadbalancer-1"
        target_group = "target-group-1"
        grid_pos = GridPos(1, 2, 3, 4)
        notifications = ["foo", "bar", "baz"]

        panel = generate_res_count_graph(
            name=name,
            cloudwatch_data_source=cloudwatch_data_source,
            grid_pos=grid_pos,
            loadbalancer=loadbalancer,
            target_group=target_group,
            notifications=notifications,
        )
        panel.alert.should.be.a(Alert)
        panel.alert.message.should.eql("{} has 5XX errors".format(name))
        panel.alert.alertConditions.should.have.length_of(1)
        panel.alert.alertConditions.should.eql(
            [
                AlertCondition(
                    Target(refId="A"),
                    timeRange=TimeRange("15m", "now"),
                    evaluator=GreaterThan(0),
                    reducerType=RTYPE_MAX,
                    operator=OP_AND,
                ),
            ]
        )

    def test_should_generate_error_logs_panel(self):
        name = "service-1"
        grid_pos = GridPos(1, 2, 3, 4)
        elasticsearch_data_source = "es"

        panel = generate_error_logs_panel(
            name=name,
            grid_pos=grid_pos,
            elasticsearch_data_source=elasticsearch_data_source,
        )
        panel.should.be.a(Logs)
        panel.title.should.eql("Error Logs")
        panel.gridPos.should.eql(grid_pos)
        panel.dataSource.should.eql(elasticsearch_data_source)
        panel.targets.should.have.length_of(1)
        panel.targets[0].query.should.eql(
            'tag: "{}" AND log.level: [50 TO *] AND NOT log.msg: ""'.format(name)
        )

    def test_should_generate_ecs_alb_service_dashboard(self):
        name = "service-1"
        cluster_name = "cluster-1"
        cloudwatch_data_source = "cwm"
        elasticsearch_data_source = "es"
        notifications = ["foo", "bar", "baz"]
        environment = "prod"
        max = 1000
        loadbalancer = "loadbalancer-1"
        target_group = "target-group-1"
        kibana_url = "http://kibana.example.com"

        dashboard = generate_ecs_alb_service_dashboard(
            name=name,
            cluster_name=cluster_name,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
            environment=environment,

            loadbalancer=loadbalancer,
            target_group=target_group,
            kibana_url=kibana_url,
            max=max,
            elasticsearch_data_source=elasticsearch_data_source,
        )
        dashboard.should.be.a(Dashboard)
        dashboard.title.should.eql("ECS Service: {}".format(name))
        dashboard.panels.should.have.length_of(17)
