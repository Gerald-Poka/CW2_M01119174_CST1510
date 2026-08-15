"""Chart data payload for the dashboard view.

Produces the JSON-serialised values the page's ECharts scripts consume via the
``PAGE_DATA`` global (see ``view.html`` / ``js_view.py``).
"""

import json


def build_js_data(context):
    incident_category = context["incident_category_counts"]
    incident_status = context["incident_status_counts"]
    ticket_status = context["ticket_status_counts"]
    ticket_assignee = context["ticket_assignee_counts"]
    metadata = context["filtered_metadata"]

    return {
        "incident_category": {
            "keys": json.dumps(list(incident_category.keys())),
            "values": json.dumps(list(incident_category.values())),
        },
        "incident_status": {
            "keys": json.dumps(list(incident_status.keys())),
            "values": json.dumps(list(incident_status.values())),
        },
        "ticket_status": {
            "keys": json.dumps(list(ticket_status.keys())),
            "values": json.dumps(list(ticket_status.values())),
        },
        "ticket_assignee": {
            "keys": json.dumps(list(ticket_assignee.keys())),
            "values": json.dumps(list(ticket_assignee.values())),
        },
        "metadata": {
            "keys": json.dumps([m.name for m in metadata]),
            "values": json.dumps([m.rows for m in metadata]),
        },
    }
