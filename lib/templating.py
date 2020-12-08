from grafanalib.core import Template, Templating


def get_release_template(data_source: str):
    """Get release template"""

    return Template(
        **{
            "allValue": "",
            "dataSource": data_source,
            "hide": 2,
            "includeAll": True,
            "label": "Filter by Branch/Release",
            "multi": True,
            "name": "release",
            "query": 'SELECT "release" FROM "deployment_status" WHERE $timeFilter',
            "refresh": 2,
            "sort": 1,
            "type": "query",
            "useTags": False,
        }
    )


def get_release_templating(data_source: str):
    """Get templating for release"""

    return Templating([get_release_template(data_source=data_source)])
