from grafanalib.core import (
    # Alert,
    # AlertCondition,
    # Dashboard,
    # Graph,
    # Target,
    # Annotations,
    Template,
    Templating,
)

from grafanalib.influxdb import InfluxDBTarget

from lib.elasticsearch import (
    get_elasticsearch_template,
    generate_elasticsearch_cpu_graph,
    generate_elasticsearch_dashboard,
    generate_elasticsearch_alerts_dashboard,
)

# import re


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

    def test_should_generate_elasticsearch_dashboard(self):
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
