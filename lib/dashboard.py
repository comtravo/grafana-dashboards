"""
  Dashboard decoder
"""
import json


class DashboardEncoder(json.JSONEncoder):
    """Encode dashboard objects."""

    def default(self, obj):
        to_json_data = getattr(obj, "to_json_data", None)
        if to_json_data:
            return to_json_data()
        return json.JSONEncoder.default(self, obj)
