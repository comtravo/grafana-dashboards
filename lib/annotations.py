from grafanalib.core import Annotations

from lib import colors


def get_release_annotations(data_source: str):
    """Generate release annotations

    Args:
        data_source (str): data source to find annotations in
    """

    return Annotations(
        [
            {
                "datasource": data_source,
                "enable": True,
                "hide": False,
                "iconColor": colors.GREEN,
                "limit": 100,
                "name": "Show Deployments in Graphs (green dashed line)",
                "query": 'SELECT "release" FROM "deployment_status" WHERE ("operation"=\'deploy\') AND ("result"=\'0\') AND ("release" =~ /^$release/) AND $timeFilter',
                "showIn": 0,
                "tags": [],
                "type": "tags",
            },
            {
                "datasource": data_source,
                "enable": False,
                "hide": False,
                "iconColor": colors.RED,
                "limit": 100,
                "name": "Show Failed Deployments in Graphs (red dashed line)",
                "query": 'SELECT "release" FROM "deployment_status" WHERE ("operation"=\'deploy\') AND ("result"=\'2\') AND ("release" =~ /^$release/) AND $timeFilter',
                "showIn": 0,
                "tags": [],
                "type": "tags Deployments in Graphs",
            },
            {
                "datasource": data_source,
                "enable": False,
                "hide": False,
                "iconColor": colors.ORANGE,
                "limit": 100,
                "name": "Show Aborted Deployments in Graphs (orange dashed line)",
                "query": 'SELECT "release" FROM "deployment_status" WHERE ("operation"=\'deploy\') AND ("result"=\'1\') AND ("release" =~ /^$release/) AND $timeFilter',
                "showIn": 0,
                "tags": [],
                "type": "tags",
            },
        ]
    )
