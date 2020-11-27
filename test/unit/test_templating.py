from grafanalib.core import Templating
from lib.templating import get_release_template


class TestGetReleaseTemplate:
    """Test get_release_template"""

    def test_should_generate_release_template_object(self):
        """should generate proper release template object"""

        expected_query = 'SELECT "release" FROM "deployment_status" WHERE $timeFilter'
        expected_data_source = "prod"

        release_template_object = get_release_template(data_source=expected_data_source)
        release_template_object.should.be.a(Templating)
        release_template_object.to_json_data()["list"].should.have.length_of(1)

        actual_template_object = release_template_object.to_json_data()["list"][0]

        actual_template_object["datasource"].should.equal(expected_data_source)
        actual_template_object["definition"].should.equal(expected_query)
        actual_template_object["query"].should.equal(expected_query)
        actual_template_object["type"].should.equal("query")
        actual_template_object["name"].should.equal("release")
