# agent_v2/monitoring.py

"""
Cybersecurity monitoring utilities.

These functions perform read-only checks against the existing SQLite
database to identify important conditions, such as:

- New Critical incidents
- Open Critical incidents
- High-priority unresolved IT tickets
- Incident categories with unusually high counts

They return structured "alerts" that can be displayed in Streamlit.
"""

from typing import List, Dict, Any
from agent_v2.tools import incident_tools, ticket_tools, analytics_tools


def check_new_critical_incidents() -> List[Dict[str, Any]]:
    """
    Detect critical incidents that are in an 'Open' or 'In Progress'-like state.

    NOTE:
    Your schema's 'status' set is:
      - Open
      - Resolved
      - Closed
    but your admin page uses an extra 'In Progress'.

    This function treats "Open" and "In Progress" (if present) as 'new/active'.

    Returns:
        List of alert dicts:
        {
            "alert_type": "new_critical_incident",
            "severity": "high",
            "incident_id": int,
            "description": str,
            "status": str,
            "category": str,
            "recommended_action": str,
        }
    """
    alerts: List[Dict[str, Any]] = []

    # Get all critical incidents, regardless of status
    critical_incidents = incident_tools.search_incidents(severity="Critical")

    for inc in critical_incidents:
        status = inc.get("status")
        if status in ("Open", "In Progress"):
            alerts.append(
                {
                    "alert_type": "new_critical_incident",
                    "severity": "high",
                    "incident_id": inc.get("incident_id"),
                    "description": inc.get("description", ""),
                    "status": status,
                    "category": inc.get("category", ""),
                    "recommended_action": "Review and triage this critical incident immediately.",
                }
            )

    return alerts


def check_unresolved_critical_incidents() -> List[Dict[str, Any]]:
    """
    Detect Critical incidents that are not yet Resolved or Closed.

    Returns:
        List of alert dicts:
        {
            "alert_type": "unresolved_critical_incident",
            "severity": "critical",
            "incident_id": int,
            "description": str,
            "status": str,
            "category": str,
            "recommended_action": str,
        }
    """
    alerts: List[Dict[str, Any]] = []

    # We consider "Open" and "In Progress" as unresolved.
    critical_open = incident_tools.search_incidents(severity="Critical", status="Open")
    # 'In Progress' isn't in your original schema list, but admin page offers it,
    # so we manually query for it using the same search + filter pattern.
    critical_in_progress = [
        inc
        for inc in incident_tools.search_incidents(severity="Critical")
        if inc.get("status") == "In Progress"
    ]

    for inc in critical_open + critical_in_progress:
        alerts.append(
            {
                "alert_type": "unresolved_critical_incident",
                "severity": "critical",
                "incident_id": inc.get("incident_id"),
                "description": inc.get("description", ""),
                "status": inc.get("status", ""),
                "category": inc.get("category", ""),
                "recommended_action": "Escalate and ensure ownership for this critical unresolved incident.",
            }
        )

    return alerts


def check_high_priority_tickets() -> List[Dict[str, Any]]:
    """
    Detect high-priority IT tickets that are still Open.

    Returns:
        List of alert dicts:
        {
            "alert_type": "high_priority_ticket",
            "severity": "medium",
            "ticket_id": int,
            "description": str,
            "status": str,
            "priority": str,
            "assigned_to": str,
            "recommended_action": str,
        }
    """
    alerts: List[Dict[str, Any]] = []

    high_open_tickets = [
        t for t in ticket_tools.search_tickets(priority="High", status="Open")
    ]

    for ticket in high_open_tickets:
        alerts.append(
            {
                "alert_type": "high_priority_ticket",
                "severity": "medium",
                "ticket_id": ticket.get("ticket_id"),
                "description": ticket.get("description", ""),
                "status": ticket.get("status", ""),
                "priority": ticket.get("priority", ""),
                "assigned_to": ticket.get("assigned_to", ""),
                "recommended_action": "Review and ensure this high-priority ticket is being actively worked on.",
            }
        )

    return alerts


def check_incident_category_spikes(threshold: int = 10) -> List[Dict[str, Any]]:
    """
    Detect incident categories with unusually high counts.

    'Unusual' is approximated by a simple threshold on count.

    Parameters:
        threshold: Minimum number of incidents in a category to trigger an alert.

    Returns:
        List of alert dicts:
        {
            "alert_type": "incident_category_spike",
            "severity": "medium" | "high",
            "category": str,
            "count": int,
            "recommended_action": str,
        }
    """
    alerts: List[Dict[str, Any]] = []

    category_stats = analytics_tools.get_incident_category_statistics()

    for category, count in category_stats.items():
        if count >= threshold:
            severity = "high" if count >= threshold * 2 else "medium"
            alerts.append(
                {
                    "alert_type": "incident_category_spike",
                    "severity": severity,
                    "category": category,
                    "count": count,
                    "recommended_action": (
                        "Investigate why this category has a high number of incidents. "
                        "Look for root causes and mitigation strategies."
                    ),
                }
            )

    return alerts


def generate_monitoring_summary(threshold: int = 10) -> Dict[str, Any]:
    """
    Run all monitoring checks and return a structured summary.

    Parameters:
        threshold: Threshold for category spike detection.

    Returns:
        {
            "alerts": [ ... ],   # list of all alerts from all checks
            "totals": {
                "new_critical_incidents": int,
                "unresolved_critical_incidents": int,
                "high_priority_tickets": int,
                "category_spikes": int,
            }
        }
    """
    alerts: List[Dict[str, Any]] = []

    new_crit = check_new_critical_incidents()
    unresolved_crit = check_unresolved_critical_incidents()
    high_tickets = check_high_priority_tickets()
    spikes = check_incident_category_spikes(threshold=threshold)

    alerts.extend(new_crit)
    alerts.extend(unresolved_crit)
    alerts.extend(high_tickets)
    alerts.extend(spikes)

    summary = {
        "alerts": alerts,
        "totals": {
            "new_critical_incidents": len(new_crit),
            "unresolved_critical_incidents": len(unresolved_crit),
            "high_priority_tickets": len(high_tickets),
            "category_spikes": len(spikes),
        },
    }

    return summary
