from grafanalib.core import Templating
from lib.templating import get_release_templating


class TestGetReleaseTemplate:
    """Test get_release_templating"""

    def test_should_generate_release_template_object(self):
        """should generate proper release template object"""

        expected_query = 'SELECT "release" FROM "deployment_status" WHERE $timeFilter'
        expected_data_source = "prod"

        release_template_object = get_release_templating(
            data_source=expected_data_source
        )
        release_template_object.should.be.a(Templating)
        release_template_object.list.should.have.length_of(1)

        release_template_object.list[0].dataSource.should.equal(expected_data_source)
        release_template_object.list[0].query.should.equal(expected_query)
        release_template_object.list[0].type.should.equal("query")
        release_template_object.list[0].name.should.equal("release")
