ALERT_THRESHOLD = False
ALERT_REF_ID = "A"
TIMEZONE = ""
SHARED_CROSSHAIR = True
EDITABLE = False
TRANSPARENT = True
RAW_QUERY = True
RETENTION_POLICY = "autogen"


def get_documentation_link(url: str):
    return {"targetBlank": True, "title": "Link to Documentation", "url": url}


def get_series_overrides(min_alias: str, mean_alias: str, max_alias: str):
    return [
        {"alias": min_alias, "color": "#C8F2C2", "lines": False},
        {"alias": mean_alias, "color": "#FADE2A", "fill": 0},
        {
            "alias": max_alias,
            "color": "rgb(77, 159, 179)",
            "fillBelowTo": min_alias,
            "lines": False,
        },
    ]
