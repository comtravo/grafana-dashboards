from grafanalib.core import (
    Alert,
    Graph,
    Template,
    Templating,
)

from grafanalib.cloudwatch import CloudwatchMetricsTarget

from lib.elasticache_redis import (
    generate_elasticache_redis_connections_graph,
    generate_elasticache_redis_cpu_usage_graph,
    generate_elasticache_redis_latency_graph,
    generate_elasticache_redis_memory_usage_graph,
    generate_elasticache_redis_network_in_graph,
    generate_elasticache_redis_network_out_graph,
    generate_elasticache_redis_replication_graph,
    generate_elasticache_redis_dashboard,
)


class TestElasticCacheRedisDashboard:
    def test_should_generate_elasticache_redis_memory_usage_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_memory_usage_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Memory usage")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(4)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.period.should.equal("1m")
            target.statistics.should.equal(["Maximum"])
            target.dimensions.should.equal(
                {"CacheClusterId": cache_cluster_id}
            )

        generated_graph.targets[0].metricName.should.equal("BytesUsedForCache")
        generated_graph.targets[1].metricName.should.equal(
            "DatabaseMemoryUsagePercentage"
        )
        generated_graph.targets[2].metricName.should.equal("SwapUsage")
        generated_graph.targets[3].metricName.should.equal("Evictions")


    def test_should_generate_elasticache_redis_cpu_usage_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_cpu_usage_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=[]
        )
        generated_graph.title.should.match(r"CPU utilization")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(3)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.namespace.should.equal("AWS/ElastiCache")
            target.period.should.equal("1m")
            target.dimensions.should.equal(
                {"CacheClusterId": cache_cluster_id}
            )

        generated_graph.targets[0].metricName.should.equal("CPUCreditBalance")
        generated_graph.targets[0].statistics.should.equal(["Minimum"])
        generated_graph.targets[1].metricName.should.equal("CPUCreditUsage")
        generated_graph.targets[1].statistics.should.equal(["Maximum"])
        generated_graph.targets[2].metricName.should.equal("EngineCPUUtilization")
        generated_graph.targets[2].statistics.should.equal(["Maximum"])


    def test_should_generate_elasticache_cpu_usage_graph_with_notifications(
        self,
    ):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["foo", "bar"]
        generated_graph = generate_elasticache_redis_cpu_usage_graph(
            cache_cluster_id=cache_cluster_id,
            notifications=notifications,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)


    def test_should_generate_elasticsearch_dashboard(self):

        name = "ElastiCache Redis"
        cache_cluster_id = "1234567890"
        environment = "prod"
        influxdb_data_source = "influxdb"
        cloudwatch_data_source = "cw"
        notifications = ["slack-1", "slack-2"]

        generated_dashboard = generate_elasticache_redis_dashboard(
            cache_cluster_id=cache_cluster_id,
            environment=environment,
            influxdb_data_source=influxdb_data_source,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )

        generated_dashboard.title.should.equal(name)
        generated_dashboard.templating.should.be.a(Templating)
        generated_dashboard.templating.list.should.have.length_of(1)
        generated_dashboard.templating.list[0].should.be.a(Template)
        generated_dashboard.tags.should.have.length_of(3)
        generated_dashboard.rows.should.have.length_of(3)
        generated_dashboard.links.should.have.length_of(1)
