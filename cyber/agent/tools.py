from datetime import datetime

from django.db.models import Avg, Count

from cyber.models import (
    CyberIncidents,
    ItTickets,
    DatasetsMetadata,
)


def _to_dict(instance):
    return {
        field.name: getattr(instance, field.name)
        for field in instance._meta.fields
    }


# ---------------------------------------------------------------------------
# Incident tools
# ---------------------------------------------------------------------------

def search_incidents(severity=None, status=None, category=None):
    qs = CyberIncidents.objects.all()
    if severity:
        qs = qs.filter(severity=severity)
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category=category)
    return [_to_dict(i) for i in qs]


def get_incident(incident_id):
    try:
        return _to_dict(CyberIncidents.objects.get(incident_id=incident_id))
    except (CyberIncidents.DoesNotExist, TypeError, ValueError):
        return None


def get_incident_statistics():
    from django.db.models import Count, Q
    agg = CyberIncidents.objects.aggregate(
        total=Count("incident_id"),
    )
    statuses = dict(
        CyberIncidents.objects.values_list("status").annotate(c=Count("incident_id"))
    )
    severities = dict(
        CyberIncidents.objects.values_list("severity").annotate(c=Count("incident_id"))
    )
    return {
        "total_incidents": agg["total"],
        "open_incidents": statuses.get("Open", 0),
        "resolved_incidents": statuses.get("Resolved", 0),
        "closed_incidents": statuses.get("Closed", 0),
        "critical_incidents": severities.get("Critical", 0),
        "high_incidents": severities.get("High", 0),
        "medium_incidents": severities.get("Medium", 0),
        "low_incidents": severities.get("Low", 0),
    }


# ---------------------------------------------------------------------------
# Ticket tools
# ---------------------------------------------------------------------------

def search_tickets(priority=None, status=None, assigned_to=None):
    qs = ItTickets.objects.all()
    if priority:
        qs = qs.filter(priority=priority)
    if status:
        qs = qs.filter(status=status)
    if assigned_to:
        qs = qs.filter(assigned_to=assigned_to)
    return [_to_dict(t) for t in qs]


def get_ticket(ticket_id):
    try:
        return _to_dict(ItTickets.objects.get(ticket_id=ticket_id))
    except (ItTickets.DoesNotExist, TypeError, ValueError):
        return None


def get_ticket_statistics():
    statuses = dict(
        ItTickets.objects.values_list("status").annotate(c=Count("ticket_id"))
    )
    priorities = dict(
        ItTickets.objects.values_list("priority").annotate(c=Count("ticket_id"))
    )
    avg = ItTickets.objects.filter(
        resolution_time_hours__isnull=False
    ).aggregate(avg=Avg("resolution_time_hours"))["avg"]
    return {
        "total_tickets": ItTickets.objects.count(),
        "open_tickets": statuses.get("Open", 0),
        "resolved_tickets": statuses.get("Resolved", 0),
        "closed_tickets": statuses.get("Closed", 0),
        "high_priority": priorities.get("High", 0),
        "medium_priority": priorities.get("Medium", 0),
        "low_priority": priorities.get("Low", 0),
        "average_resolution_time": float(avg) if avg is not None else None,
    }


# ---------------------------------------------------------------------------
# Dataset metadata tools
# ---------------------------------------------------------------------------

def search_datasets(uploaded_by=None):
    qs = DatasetsMetadata.objects.all()
    if uploaded_by:
        qs = qs.filter(uploaded_by=uploaded_by)
    return [_to_dict(d) for d in qs]


def get_dataset(dataset_id):
    try:
        return _to_dict(DatasetsMetadata.objects.get(dataset_id=dataset_id))
    except (DatasetsMetadata.DoesNotExist, TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Analytics tools
# ---------------------------------------------------------------------------

def get_dashboard_summary():
    statuses = dict(
        CyberIncidents.objects.values_list("status").annotate(c=Count("incident_id"))
    )
    severities = dict(
        CyberIncidents.objects.values_list("severity").annotate(c=Count("incident_id"))
    )
    ticket_statuses = dict(
        ItTickets.objects.values_list("status").annotate(c=Count("ticket_id"))
    )
    ticket_priorities = dict(
        ItTickets.objects.values_list("priority").annotate(c=Count("ticket_id"))
    )
    return {
        "total_incidents": CyberIncidents.objects.count(),
        "critical_incidents": severities.get("Critical", 0),
        "high_incidents": severities.get("High", 0),
        "open_incidents": statuses.get("Open", 0),
        "total_tickets": ItTickets.objects.count(),
        "open_tickets": ticket_statuses.get("Open", 0),
        "high_priority_tickets": ticket_priorities.get("High", 0),
        "total_datasets": DatasetsMetadata.objects.count(),
    }


def get_incident_category_statistics():
    return dict(
        CyberIncidents.objects.values_list("category").annotate(c=Count("incident_id"))
    )


def get_ticket_workload():
    all_by = dict(
        ItTickets.objects.values_list("assigned_to").annotate(c=Count("ticket_id"))
    )
    open_by = dict(
        ItTickets.objects.filter(status="Open")
        .values_list("assigned_to")
        .annotate(c=Count("ticket_id"))
    )
    return {
        "tickets_by_assignee": all_by,
        "open_tickets_by_assignee": open_by,
    }


# ---------------------------------------------------------------------------
# Controlled write tools (executed only after admin confirmation)
# ---------------------------------------------------------------------------

def create_incident(timestamp=None, severity=None, category=None, status=None,
                    description=None):
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    from cyber.services import add_cyber_incident
    return add_cyber_incident(timestamp, severity, category, status, description)


def update_incident(incident_id, updates):
    allowed = {"timestamp", "severity", "category", "status", "description"}
    updated = CyberIncidents.objects.filter(
        incident_id=incident_id
    ).update(**{k: v for k, v in updates.items() if k in allowed})
    return updated > 0


def close_incident(incident_id):
    return update_incident(incident_id, {"status": "Closed"})


def create_ticket(priority=None, description=None, status=None, assigned_to=None,
                  created_at=None, resolution_time=None):
    if not created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    from cyber.services import add_it_ticket
    return add_it_ticket(priority, description, status, assigned_to, created_at,
                         resolution_time)


def update_ticket(ticket_id, updates):
    allowed = {"priority", "description", "status", "assigned_to", "created_at",
               "resolution_time_hours"}
    mapped = {}
    for k, v in updates.items():
        key = "resolution_time_hours" if k == "resolution_time" else k
        if key in allowed:
            mapped[key] = v
    updated = ItTickets.objects.filter(ticket_id=ticket_id).update(**mapped)
    return updated > 0


def assign_ticket(ticket_id, assignee):
    return update_ticket(ticket_id, {"assigned_to": assignee})


def close_ticket(ticket_id):
    return update_ticket(ticket_id, {"status": "Closed"})
