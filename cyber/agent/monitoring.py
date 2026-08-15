from cyber.agent import tools


def check_new_critical_incidents():
    alerts = []
    for inc in tools.search_incidents(severity="Critical"):
        if inc.get("status") in ("Open", "In Progress"):
            alerts.append({
                "alert_type": "new_critical_incident",
                "severity": "high",
                "incident_id": inc.get("incident_id"),
                "description": inc.get("description", ""),
                "status": inc.get("status"),
                "category": inc.get("category", ""),
                "recommended_action": "Review and triage this critical incident immediately.",
            })
    return alerts


def check_unresolved_critical_incidents():
    alerts = []
    critical = tools.search_incidents(severity="Critical")
    for inc in critical:
        if inc.get("status") in ("Open", "In Progress"):
            alerts.append({
                "alert_type": "unresolved_critical_incident",
                "severity": "critical",
                "incident_id": inc.get("incident_id"),
                "description": inc.get("description", ""),
                "status": inc.get("status", ""),
                "category": inc.get("category", ""),
                "recommended_action": ("Escalate and ensure ownership for this "
                                       "critical unresolved incident."),
            })
    return alerts


def check_high_priority_tickets():
    alerts = []
    for ticket in tools.search_tickets(priority="High", status="Open"):
        alerts.append({
            "alert_type": "high_priority_ticket",
            "severity": "medium",
            "ticket_id": ticket.get("ticket_id"),
            "description": ticket.get("description", ""),
            "status": ticket.get("status", ""),
            "priority": ticket.get("priority", ""),
            "assigned_to": ticket.get("assigned_to", ""),
            "recommended_action": ("Review and ensure this high-priority ticket "
                                   "is being actively worked on."),
        })
    return alerts


def check_incident_category_spikes(threshold=10):
    alerts = []
    for category, count in tools.get_incident_category_statistics().items():
        if count >= threshold:
            severity = "high" if count >= threshold * 2 else "medium"
            alerts.append({
                "alert_type": "incident_category_spike",
                "severity": severity,
                "category": category,
                "count": count,
                "recommended_action": (
                    "Investigate why this category has a high number of incidents. "
                    "Look for root causes and mitigation strategies."
                ),
            })
    return alerts


def generate_monitoring_summary(threshold=10):
    new_crit = check_new_critical_incidents()
    unresolved_crit = check_unresolved_critical_incidents()
    high_tickets = check_high_priority_tickets()
    spikes = check_incident_category_spikes(threshold=threshold)

    alerts = new_crit + unresolved_crit + high_tickets + spikes
    return {
        "alerts": alerts,
        "totals": {
            "new_critical_incidents": len(new_crit),
            "unresolved_critical_incidents": len(unresolved_crit),
            "high_priority_tickets": len(high_tickets),
            "category_spikes": len(spikes),
        },
    }
