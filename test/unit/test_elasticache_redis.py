from grafanalib.cloudwatch import CloudwatchMetricsTarget
from grafanalib.core import (
    OP_OR,
    RTYPE_MAX,
    Alert,
    Graph,
    LowerThan,
    Template,
    Templating,
)

from lib.elasticache_redis import (
    generate_elasticache_redis_connections_graph,
    generate_elasticache_redis_cpu_credit_usage_graph,
    generate_elasticache_redis_cpu_usage_graph,
    generate_elasticache_redis_dashboard,
    generate_elasticache_redis_db_memory_usage_and_evicitons_graph,
    generate_elasticache_redis_latency_graph,
    generate_elasticache_redis_network_in_graph,
    generate_elasticache_redis_network_out_graph,
    generate_elasticache_redis_replication_graph,
    generate_elasticache_redis_swap_and_memory_usage_graph,
)


class TestElasticCacheRedisDashboard:
    def test_should_generate_elasticache_redis_db_memory_usage_and_evictions_graph(
        self,
    ):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = (
            generate_elasticache_redis_db_memory_usage_and_evicitons_graph(
                cache_cluster_id=cache_cluster_id,
                cloudwatch_data_source=cloudwatch_data_source,
            )
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"DB memory usage and Evictions")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(2)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.period.should.equal("1m")
            target.statistics.should.equal(["Maximum"])
            target.dimensions.should.equal({"CacheClusterId": cache_cluster_id})

        generated_graph.targets[0].metricName.should.equal(
            "DatabaseMemoryUsagePercentage"
        )
        generated_graph.targets[1].metricName.should.equal("Evictions")

    def test_should_generate_elasticache_redis_memory_and_swap_usage_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_swap_and_memory_usage_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Memory and Swap usage")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(2)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.period.should.equal("1m")
            target.statistics.should.equal(["Maximum"])
            target.dimensions.should.equal({"CacheClusterId": cache_cluster_id})

        generated_graph.targets[0].metricName.should.equal("BytesUsedForCache")
        generated_graph.targets[1].metricName.should.equal("SwapUsage")

    def test_should_generate_elasticache_redis_cpu_usage_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_cpu_usage_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.title.should.match(r"Engine CPU utilization")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)

        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].namespace.should.equal("AWS/ElastiCache")
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].dimensions.should.equal(
            {"CacheClusterId": cache_cluster_id}
        )
        generated_graph.targets[0].metricName.should.equal("EngineCPUUtilization")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])

    def test_should_generate_elasticache_redis_cpu_credit_usage_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_cpu_credit_usage_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=[],
        )
        generated_graph.title.should.match(r"CPU credit utilization")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(2)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.namespace.should.equal("AWS/ElastiCache")
            target.period.should.equal("1m")
            target.dimensions.should.equal({"CacheClusterId": cache_cluster_id})

        generated_graph.targets[0].metricName.should.equal("CPUCreditBalance")
        generated_graph.targets[0].statistics.should.equal(["Minimum"])
        generated_graph.targets[1].metricName.should.equal("CPUCreditUsage")
        generated_graph.targets[1].statistics.should.equal(["Maximum"])

    def test_should_generate_elasticache_cpu_credit_usage_graph_with_notifications(
        self,
    ):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        notifications = ["foo", "bar"]
        generated_graph = generate_elasticache_redis_cpu_credit_usage_graph(
            cache_cluster_id=cache_cluster_id,
            notifications=notifications,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.targets[0].refId.should.equal("A")
        generated_graph.alert.should.be.a(Alert)
        generated_graph.alert.frequency.should.equal("2m")
        generated_graph.alert.gracePeriod.should.equal("2m")
        generated_graph.alert.notifications.should.equal(notifications)
        generated_graph.alert.alertConditions[0].evaluator.should.be.equal(
            LowerThan(250)
        )
        generated_graph.alert.alertConditions[0].reducerType.should.be.equal(RTYPE_MAX)
        generated_graph.alert.alertConditions[0].operator.should.be.equal(OP_OR)

    def test_should_generate_elasticache_redis_network_in_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_network_in_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Network in")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)

        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].dimensions.should.equal(
            {"CacheClusterId": cache_cluster_id}
        )
        generated_graph.targets[0].metricName.should.equal("NetworkBytesIn")

    def test_should_generate_elasticache_redis_network_out_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_network_out_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Network out")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)

        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].dimensions.should.equal(
            {"CacheClusterId": cache_cluster_id}
        )
        generated_graph.targets[0].metricName.should.equal("NetworkBytesOut")

    def test_should_generate_elasticache_redis_connections_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_connections_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Current connections")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)

        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].dimensions.should.equal(
            {"CacheClusterId": cache_cluster_id}
        )
        generated_graph.targets[0].metricName.should.equal("CurrConnections")

    def test_should_generate_elasticache_redis_replication_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_replication_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Replication")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(2)

        for target in generated_graph.targets:
            target.should.be.a(CloudwatchMetricsTarget)
            target.period.should.equal("1m")
            target.statistics.should.equal(["Maximum"])
            target.dimensions.should.equal({"CacheClusterId": cache_cluster_id})

        generated_graph.targets[0].metricName.should.equal("ReplicationBytes")
        generated_graph.targets[1].metricName.should.equal("ReplicationLag")

    def test_should_generate_elasticache_redis_latency_graph(self):

        cache_cluster_id = "1234567890"
        cloudwatch_data_source = "cw"
        generated_graph = generate_elasticache_redis_latency_graph(
            cache_cluster_id=cache_cluster_id,
            cloudwatch_data_source=cloudwatch_data_source,
        )
        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Latency")
        generated_graph.dataSource.should.match(cloudwatch_data_source)
        generated_graph.targets.should.have.length_of(1)

        generated_graph.targets[0].should.be.a(CloudwatchMetricsTarget)
        generated_graph.targets[0].period.should.equal("1m")
        generated_graph.targets[0].statistics.should.equal(["Maximum"])
        generated_graph.targets[0].dimensions.should.equal(
            {"CacheClusterId": cache_cluster_id}
        )
        generated_graph.targets[0].metricName.should.equal("StringBasedCmdsLatency")

    def test_should_generate_elasticsearch_dashboard(self):

        name = "foo"
        cache_cluster_id = "1234567890"
        environment = "prod"
        influxdb_data_source = "influxdb"
        cloudwatch_data_source = "cw"
        notifications = ["slack-1", "slack-2"]

        generated_dashboard = generate_elasticache_redis_dashboard(
            name=name,
            cache_cluster_id=cache_cluster_id,
            environment=environment,
            influxdb_data_source=influxdb_data_source,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
        )

        generated_dashboard.title.should.equal("ElastiCache Redis: foo")
        generated_dashboard.tags.should.have.length_of(3)
        generated_dashboard.rows.should.have.length_of(3)
        generated_dashboard.links.should.have.length_of(1)
