from grafanalib.core import (
    Alert,
    Graph,
    Template,
    Templating,
)

from grafanalib.cloudwatch import CloudwatchMetricsTarget

from lib.elasticsearch import (
    generate_elasticsearch_cpu_graph,
    generate_elasticsearch_jvm_memory_pressure_graph,
    generate_elasticsearch_documents_graph,
    generate_elasticsearch_storage_graph,
    generate_elasticsearch_requests_graph,
    generate_elasticsearch_status_red_alert_graph,
    generate_elasticsearch_nodes_alert_graph,
    # generate_elasticsearch_storage_alert_graph,
    generate_elasticsearch_writes_blocked_alert_graph,
    generate_elasticsearch_automated_snapshot_failure_alert_graph,
    # generate_elasticsearch_jvm_memory_pressure_alert_graph,
    generate_elasticsearch_dashboard,
    # generate_elasticsearch_alerts_dashboard,
)


class TestElasticsearchDashboards:
    def test_should_generate_elasticsearch_cpu_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticsearch_cpu_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.title.should.match(r"CPU utilization")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].namespace.should.equal("AWS/ES")
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].metricName.should.equal("CPUUtilization")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].dimensions.should.equal(
            {"DomainName": name, "ClientId": client_id}
        )

    def test_should_generate_elasticsearch_jvm_memory_pressure_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = []
        generated_graph = generate_elasticsearch_jvm_memory_pressure_graph(
            name=name,
            client_id=client_id,
            notifications=notifications,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"JVM memory pressure")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].metricName.should.equal("JVMMemoryPressure")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].dimensions.should.equal(
            {"DomainName": name, "ClientId": client_id}
        )

    def test_should_generate_elasticsearch_jvm_memory_pressure_graph_with_notifications(
        self,
    ):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["foo", "bar"]
        generated_graph = generate_elasticsearch_jvm_memory_pressure_graph(
            name=name,
            client_id=client_id,
            notifications=notifications,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_documents_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticsearch_documents_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Documents")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(2)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.period.should.equal("1m")
            target.statistics.should.equal(["Maximum"])
            target.dimensions.should.equal({"DomainName": name, "ClientId": client_id})
        generated_graph.targets[0].metricName.should.equal("SearchableDocuments")
        generated_graph.targets[1].metricName.should.equal("DeletedDocuments")

    def test_should_generate_elasticsearch_storage_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["foo", "bar"]
        generated_graph = generate_elasticsearch_storage_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Storage")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(2)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.period.should.equal("1m")
            target.dimensions.should.equal({"DomainName": name, "ClientId": client_id})

        generated_graph.targets[0].statistics.should.equal(["Minimum"])
        generated_graph.targets[0].metricName.should.equal("FreeStorageSpace")
        generated_graph.targets[1].statistics.should.equal(["Maximum"])
        generated_graph.targets[1].metricName.should.equal("ClusterUsedSpace")
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_requests_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticsearch_requests_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Requests")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(4)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.period.should.equal("1m")
            target.dimensions.should.equal({"DomainName": name, "ClientId": client_id})
            target.statistics.should.equal(["Sum"])
            target.namespace.should.equal("AWS/ES")
        generated_graph.targets[0].metricName.should.equal("2xx")
        generated_graph.targets[1].metricName.should.equal("3xx")
        generated_graph.targets[2].metricName.should.equal("4xx")
        generated_graph.targets[3].metricName.should.equal("5xx")

    def test_should_generate_elasticsearch_status_red_alert_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_status_red_alert_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Status RED alerts")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].metricName.should.equal("ClusterStatus.red")
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].namespace.should.equal("AWS/ES")
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_nodes_alert_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_nodes_alert_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Elasticsearch node alerts")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(2)
        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].statistics.should.equal(["Minimum"])
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].namespace.should.equal("AWS/ES")
        generated_graph.targets[0].metricName.should.equal("Nodes")
        generated_graph.targets[0].dimensions.should.equal(
            {"DomainName": name, "ClientId": client_id}
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_writes_blocked_alert_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_writes_blocked_alert_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Elasticsearch write blocked alerts")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].namespace.should.equal("AWS/ES")
        generated_graph.targets[0].metricName.should.equal("ClusterIndexWritesBlocked")
        generated_graph.targets[0].dimensions.should.equal(
            {"DomainName": name, "ClientId": client_id}
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_automated_snapshot_failure_alert_graph(self):
        name = "es"
        client_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_automated_snapshot_failure_alert_graph(
            name=name,
            client_id=client_id,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(
            r"Elasticsearch automated snapshot failure alerts"
        )
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].namespace.should.equal("AWS/ES")
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].dimensions.should.equal(
            {"DomainName": name, "ClientId": client_id}
        )
        generated_graph.targets[0].metricName.should.equal("AutomatedSnapshotFailure")
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_dashboard(self):
        name = "es"
        client_id = "1234567890"
        environment = "prod"
        influxdb_data_source = "influxdb"
        cloudwatch_data_source = "cw"
        notifications = ["slack-1", "slack-2"]

        generated_dashboard = generate_elasticsearch_dashboard(
            name=name,
            client_id=client_id,
            environment=environment,
            influxdb_data_source=influxdb_data_source,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )
        generated_dashboard.title.should.equal("Elasticsearch: {}".format(name))
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.templating.list.should.have.length_of(1)
        generated_dashboard.templating.list[0].should.be.a(Template)
        generated_dashboard.tags.should.have.length_of(2)
        generated_dashboard.rows.should.have.length_of(5)
        generated_dashboard.links.should.have.length_of(1)
