from grafanalib.core import (
    Alert,
    # AlertCondition,
    # Dashboard,
    Graph,
    # Target,
    # Annotations,
    Template,
    Templating,
)

from grafanalib.influxdb import InfluxDBTarget

from lib.elasticsearch import (
    get_elasticsearch_template,
    generate_elasticsearch_cpu_graph,
    generate_elasticsearch_jvm_memory_pressure_graph,
    generate_elasticsearch_documents_graph,
    generate_elasticsearch_storage_graph,
    generate_elasticsearch_requests_graph,
    generate_elasticsearch_status_red_alert_graph,
    generate_elasticsearch_nodes_alert_graph,
    generate_elasticsearch_storage_alert_graph,
    generate_elasticsearch_writes_blocked_alert_graph,
    generate_elasticsearch_automated_snapshot_failure_alert_graph,
    generate_elasticsearch_dashboard,
    generate_elasticsearch_alerts_dashboard,
)


class TestElasticsearchDashboards:
    def test_should_get_elasticsearch_template(self):
        template = get_elasticsearch_template(data_source="prod")
        template.name.should.equal("elasticsearch")
        template.label.should.equal("Elasticsearch")
        template.query.should.equal(
            'SHOW TAG VALUES WITH KEY = "domain_name" WHERE $timeFilter'
        )
        template.multi.should.equal(False)
        template.includeAll.should.equal(False)

    def test_should_generate_elasticsearch_cpu_graph(self):
        data_source = "prod"
        generated_graph = generate_elasticsearch_cpu_graph(data_source=data_source)
        generated_graph.title.should.match(r"CPU utilization")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT max("cpu_utilization_maximum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'
        )

    def test_should_generate_elasticsearch_jvm_memory_pressure_graph(self):
        data_source = "prod"
        generated_graph = generate_elasticsearch_jvm_memory_pressure_graph(
            data_source=data_source
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"JVM memory pressure")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT max("jvm_memory_pressure_maximum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'
        )

    def test_should_generate_elasticsearch_documents_graph(self):
        data_source = "prod"
        generated_graph = generate_elasticsearch_documents_graph(
            data_source=data_source
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Documents")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(2)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT max("searchable_documents_maximum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'
        )
        generated_graph.targets[1].should.be.a(InfluxDBTarget)
        generated_graph.targets[1].query.should.equal(
            'SELECT max("deleted_documents_maximum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'
        )

    def test_should_generate_elasticsearch_storage_graph(self):
        data_source = "prod"
        generated_graph = generate_elasticsearch_storage_graph(data_source=data_source)
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Storage")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(2)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT min("free_storage_space_minimum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'
        )
        generated_graph.targets[1].should.be.a(InfluxDBTarget)
        generated_graph.targets[1].query.should.equal(
            'SELECT max("cluster_used_space_maximum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(previous)'
        )

    def test_should_generate_elasticsearch_requests_graph(self):
        data_source = "prod"
        generated_graph = generate_elasticsearch_requests_graph(data_source=data_source)
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Requests")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(4)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT max("2xx_sum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'
        )
        generated_graph.targets[1].should.be.a(InfluxDBTarget)
        generated_graph.targets[1].query.should.equal(
            'SELECT max("3xx_sum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'
        )
        generated_graph.targets[2].should.be.a(InfluxDBTarget)
        generated_graph.targets[2].query.should.equal(
            'SELECT max("4xx_sum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'
        )
        generated_graph.targets[3].should.be.a(InfluxDBTarget)
        generated_graph.targets[3].query.should.equal(
            'SELECT max("5xx_sum") FROM "autogen"."cloudwatch_aws_es" WHERE ("domain_name" =~ /^$elasticsearch$/) AND $timeFilter GROUP BY time(1m) fill(0)'
        )

    def test_should_generate_elasticsearch_status_red_alert_graph(self):
        data_source = "prod"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_status_red_alert_graph(
            data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Status RED alerts")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT max("cluster_status.red_maximum") AS "status_red" FROM "autogen"."cloudwatch_aws_es" WHERE $timeFilter GROUP BY time(1m),"domain_name" fill(previous)'
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_nodes_alert_graph(self):
        data_source = "prod"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_nodes_alert_graph(
            data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Elasticsearch node alerts")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT min("nodes_minimum") AS "nodes" FROM "autogen"."cloudwatch_aws_es" WHERE $timeFilter GROUP BY time(1m),"domain_name" fill(previous)'
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_storage_alert_graph(self):
        data_source = "prod"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_storage_alert_graph(
            data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Elasticsearch storage alerts")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT min("free_storage_space_minimum") AS "free_storage" FROM "autogen"."cloudwatch_aws_es" WHERE $timeFilter GROUP BY time(1m),"domain_name" fill(previous)'
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_writes_blocked_alert_graph(self):
        data_source = "prod"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_writes_blocked_alert_graph(
            data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Elasticsearch write blocked alerts")
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT max("cluster_index_writes_blocked_maximum") AS "writes_blocked" FROM "autogen"."cloudwatch_aws_es" WHERE $timeFilter GROUP BY time(1m),"domain_name" fill(previous)'
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_automated_snapshot_failure_alert_graph(self):
        data_source = "prod"
        notifications = ["slack-1", "slack-2"]

        generated_graph = generate_elasticsearch_automated_snapshot_failure_alert_graph(
            data_source=data_source, notifications=notifications
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(
            r"Elasticsearch automated snapshot failure alerts"
        )
        generated_graph.dataSource.should.match(data_source)
        generated_graph.targets.should.have.length_of(1)
        generated_graph.targets[0].should.be.a(InfluxDBTarget)
        generated_graph.targets[0].query.should.equal(
            'SELECT max("automated_snapshot_failure_maximum") AS "automated_snapshot_failures" FROM "autogen"."cloudwatch_aws_es" WHERE $timeFilter GROUP BY time(1m),"domain_name" fill(previous)'
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)

    def test_should_generate_elasticsearch_dashboard(self):
        data_source = "prod"
        environment = "prod"

        generated_dashboard = generate_elasticsearch_dashboard(
            data_source=data_source, environment=environment
        )
        generated_dashboard.title.should.equal("Elasticsearch")
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.templating.list.should.have.length_of(2)
        generated_dashboard.templating.list[0].should.be.a(Template)
        generated_dashboard.templating.list[1].should.be.a(Template)
        generated_dashboard.tags.should.have.length_of(2)
        generated_dashboard.rows.should.have.length_of(4)
        generated_dashboard.links.should.have.length_of(1)

    def test_should_generate_elasticsearch_alerts_dashboard(self):
        data_source = "prod"
        environment = "prod"
        notifications = ["lorem", "ipsum"]

        generated_dashboard = generate_elasticsearch_alerts_dashboard(
            data_source=data_source,
            environment=environment,
            notifications=notifications,
        )
        generated_dashboard.title.should.equal("Elasticsearch Alerts")
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.templating.list.should.have.length_of(1)
        generated_dashboard.templating.list[0].should.be.a(Template)
        generated_dashboard.tags.should.have.length_of(2)
        generated_dashboard.rows.should.have.length_of(3)
        generated_dashboard.links.should.have.length_of(1)

    def test_should_raise_exception_when_notifications_is_empty(self):
        data_source = "prod"
        environment = "prod"
        notifications = []

        generate_elasticsearch_alerts_dashboard.when.called_with(
            data_source=data_source,
            environment=environment,
            notifications=notifications,
        ).should.throw(Exception, r"Notifications is None")
