"""Dashboard context assembly.

Separates data gathering (this module) from request handling (``index.py``)
and from chart/JS payload generation (``_js_index.py`` / ``js_view.py``).
"""

from cyber import services
from cyber.features.dashboard import _js_index


def build_context(request):
    incidents = list(services.get_all_cyber_incidents())
    tickets = list(services.get_all_it_tickets())
    metadata = list(services.get_all_datasets_metadata())

    severities = sorted({i.severity for i in incidents if i.severity})
    priorities = sorted({t.priority for t in tickets if t.priority})
    uploaders = sorted({m.uploaded_by for m in metadata if m.uploaded_by})

    severity = request.GET.get("severity", severities[0] if severities else "")
    priority = request.GET.get("priority", priorities[0] if priorities else "")
    uploaded_by = request.GET.get("uploaded_by", uploaders[0] if uploaders else "")

    # Cyber incidents (filtered by severity)
    filtered_incidents = [i for i in incidents if i.severity == severity]
    incident_status_counts = {}
    incident_category_counts = {}
    for i in filtered_incidents:
        incident_status_counts[i.status] = incident_status_counts.get(i.status, 0) + 1
        incident_category_counts[i.category] = incident_category_counts.get(i.category, 0) + 1
    incident_action = [i for i in filtered_incidents if i.status in ("Open", "In Progress")]

    # IT tickets (filtered by priority)
    filtered_tickets = [t for t in tickets if t.priority == priority]
    ticket_status_counts = {}
    ticket_assignee_counts = {}
    for t in filtered_tickets:
        ticket_status_counts[t.status] = ticket_status_counts.get(t.status, 0) + 1
        ticket_assignee_counts[t.assigned_to] = ticket_assignee_counts.get(t.assigned_to, 0) + 1
    ticket_action = [t for t in filtered_tickets if t.status in ("Open", "In Progress")]

    # Metadata (filtered by uploader)
    filtered_metadata = [m for m in metadata if m.uploaded_by == uploaded_by]
    total_rows = sum(m.rows or 0 for m in filtered_metadata)
    avg_rows = int(total_rows / len(filtered_metadata)) if filtered_metadata else 0
    largest = max(filtered_metadata, key=lambda m: m.rows or 0) if filtered_metadata else None

    context = {
        "username": request.session.get("username"),
        "role": request.session.get("role"),
        "active": "dashboard",
        "severities": severities,
        "priorities": priorities,
        "uploaders": uploaders,
        "severity": severity,
        "priority": priority,
        "uploaded_by": uploaded_by,
        "incident_count": len(filtered_incidents),
        "incident_top_category": (
            max(incident_category_counts.items(), key=lambda x: x[1])[0]
            if incident_category_counts else "-"),
        "incident_status_counts": incident_status_counts,
        "incident_category_counts": incident_category_counts,
        "incident_open": incident_status_counts.get("Open", 0),
        "incident_in_progress": incident_status_counts.get("In Progress", 0),
        "incident_action": incident_action,
        "filtered_incidents": filtered_incidents,
        "ticket_count": len(filtered_tickets),
        "ticket_top_assignee": (
            max(ticket_assignee_counts.items(), key=lambda x: x[1])[0]
            if ticket_assignee_counts else "-"),
        "ticket_status_counts": ticket_status_counts,
        "ticket_assignee_counts": ticket_assignee_counts,
        "ticket_open": ticket_status_counts.get("Open", 0),
        "ticket_in_progress": ticket_status_counts.get("In Progress", 0),
        "ticket_action": ticket_action,
        "filtered_tickets": filtered_tickets,
        "metadata_count": len(filtered_metadata),
        "total_rows": total_rows,
        "avg_rows": avg_rows,
        "largest": largest,
        "filtered_metadata": filtered_metadata,
    }
    context["js_data"] = _js_index.build_js_data(context)
    return context
