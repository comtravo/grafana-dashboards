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

# from grafanalib.influxdb import InfluxDBTarget

from lib.elasticsearch import (
    generate_elasticsearch_dashboard,
    generate_elasticsearch_alerts_dashboard,
)

import re


class TestElasticsearchDashboards:
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
