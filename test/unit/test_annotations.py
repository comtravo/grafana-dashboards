from grafanalib.core import Annotations

from lib.annotations import get_release_annotations


class TestGetReleaseAnnotations:
    """Test get_release_annotations"""

    def test_should_generate_release_annotations_object(self):
        """should generate proper release annotations object"""

        expected_queries = [
            'SELECT "release" FROM "deployment_status" WHERE ("operation"=\'deploy\') AND ("result"=\'0\') AND ("release" =~ /^$release/) AND $timeFilter',
            'SELECT "release" FROM "deployment_status" WHERE ("operation"=\'deploy\') AND ("result"=\'2\') AND ("release" =~ /^$release/) AND $timeFilter',
            'SELECT "release" FROM "deployment_status" WHERE ("operation"=\'deploy\') AND ("result"=\'1\') AND ("release" =~ /^$release/) AND $timeFilter',
        ]

        expected_data_source = "prod"

        release_annotations_object = get_release_annotations(data_source=expected_data_source)
        release_annotations_object.should.be.a(Annotations)
        release_annotations_object.to_json_data()["list"].should.have.length_of(3)

        for annotation in release_annotations_object.to_json_data()["list"]:
            annotation["query"].should.be.within(expected_queries)
            annotation["datasource"].should.be.equal(expected_data_source)
            annotation["enable"].should.be.within([True, False])
            annotation["hide"].should.be.equal(False)
            annotation["limit"].should.be.equal(100)
