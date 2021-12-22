from grafanalib.core import Dashboard, Graph, Template

from lib.firehose import (
    generate_firehose_dashboard,
    generate_firehose_graph,
    get_firehose_template,
)


class TestFirehose:
    def test_should_generate_firehose_template(self):
        influxdb_data_source = "prod"
        generated_template = get_firehose_template(influxdb_data_source)

        generated_template.should.be.a(Template)
        generated_template.name.should.eql("firehose")
        generated_template.query.should.eql(
            'SHOW TAG VALUES WITH KEY = "delivery_stream_name" WHERE $timeFilter'
        )
        generated_template.dataSource.should.eql(influxdb_data_source)
        generated_template.label.should.eql("Firehose")
        generated_template.multi.should.eql(True)
        generated_template.includeAll.should.eql(True)

    def test_should_generate_firehose_template(self):
        influxdb_data_source = "prod"
        generated_graph = generate_firehose_graph(influxdb_data_source=influxdb_data_source)

        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Firehose:")
        generated_graph.targets.should.have.length_of(3)

    def test_should_generate_firehose_dashboard(self):
        influxdb_data_source = "prod"
        environment = "prod"
        generated_dashboard = generate_firehose_dashboard(
            influxdb_data_source=influxdb_data_source, environment=environment
        )

        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.eql("Firehose")
        generated_dashboard.tags.should.eql(["firehose", environment])
        generated_dashboard.rows.should.have.length_of(1)
        generated_dashboard.rows[0].title.should.eql("$firehose")
        generated_dashboard.rows[0].repeat.should.eql("firehose")
