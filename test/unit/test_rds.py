from grafanalib.core import Alert, Dashboard, Graph, Template, Templating

from lib.rds import generate_rds_dashboard


class TestRDSMySqlDashboard:
    def test_should_generate_rds_mysql_dashboard(self):
        name = "api"
        environment = "prod"
        influxdb_data_source = "prod"
        cloudwatch_data_source = "cw"
        engine = "mysql"
        notifications = ["lorem", "ipsum"]

        generated_dashboard = generate_rds_dashboard(
            name=name,
            environment=environment,
            influxdb_data_source=influxdb_data_source,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
            engine=engine,
        )
        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.match(r"RDS: api")
        generated_dashboard.tags.should.have.length_of(4)
        generated_dashboard.tags.sort().should.equal(
            ["rds", engine, environment, "database"].sort()
        )
        generated_dashboard.links.should.have.length_of(1)
        generated_dashboard.rows.should.have.length_of(3)


class TestRDSPostgresDashboard:
    def test_should_generate_rds_mysql_dashboard(self):
        name = "api"
        environment = "prod"
        influxdb_data_source = "prod"
        cloudwatch_data_source = "cw"
        engine = "postgres"
        notifications = ["lorem", "ipsum"]

        generated_dashboard = generate_rds_dashboard(
            name=name,
            environment=environment,
            influxdb_data_source=influxdb_data_source,
            cloudwatch_data_source=cloudwatch_data_source,
            notifications=notifications,
            engine=engine,
        )
        generated_dashboard.should.be.a(Dashboard)
        generated_dashboard.title.should.match(r"RDS: api")
        generated_dashboard.tags.should.have.length_of(4)
        generated_dashboard.tags.sort().should.equal(
            ["rds", engine, environment, "database"].sort()
        )
        generated_dashboard.links.should.have.length_of(1)
        generated_dashboard.rows.should.have.length_of(4)
