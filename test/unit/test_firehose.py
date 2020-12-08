from lib.firehose import (
    get_firehose_template,
    generate_firehose_graph,
    generate_firehose_dashboard,
)

from grafanalib.core import Dashboard, Graph, Template


class TestFirehose:
    def test_should_generate_firehose_template(self):
        data_source = "prod"
        generated_template = get_firehose_template(data_source)

        generated_template.should.be.a(Template)
        generated_template.name.should.eql("firehose")
        generated_template.query.should.eql(
            'SHOW TAG VALUES WITH KEY = "delivery_stream_name" WHERE $timeFilter'
        )
        generated_template.dataSource.should.eql(data_source)
        generated_template.label.should.eql("Firehose")
        generated_template.multi.should.eql(True)
        generated_template.includeAll.should.eql(True)

    def test_should_generate_firehose_template(self):
        data_source = "prod"
        generated_graph = generate_firehose_graph(data_source=data_source)

        generated_graph.should.be.a(Graph)
        generated_graph.title.should.match(r"Firehose:")
        generated_graph.targets.should.have.length_of(3)

    def test_should_generate_firehose_dashboard(self):
        data_source = "prod"
        environment = "prod"
        generated_dashboard = generate_firehose_dashboard(
            data_source=data_source, environment=environment
        )

        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.eql("Firehose")
        generated_dashboard.tags.should.eql(["firehose", environment])
        generated_dashboard.rows.should.have.length_of(1)
        generated_dashboard.rows[0].title.should.eql("$firehose")
        generated_dashboard.rows[0].repeat.should.eql("firehose")