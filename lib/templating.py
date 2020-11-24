from grafanalib.core import Templating


def get_release_template(data_source: str):
    """Get templating for release

    Args:
        data_source (str): Data source to populate the release variable
    """

    return Templating(
        [
            {
                "allValue": "",
                "current": {"text": "All", "value": ["$__all"]},
                "datasource": data_source,
                "definition": 'SELECT "release" FROM "deployment_status" WHERE $timeFilter',
                "hide": 2,
                "includeAll": True,
                "label": "Filter by Branch/Release",
                "multi": True,
                "name": "release",
                "options": [],
                "query": 'SELECT "release" FROM "deployment_status" WHERE $timeFilter',
                "refresh": 2,
                "regex": "",
                "skipUrlSync": False,
                "sort": 1,
                "tagValuesQuery": "",
                "tags": [],
                "tagsQuery": "",
                "type": "query",
                "useTags": False,
            }
        ]
    )
