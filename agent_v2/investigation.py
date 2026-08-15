# agent_v2/investigation.py

"""
Multi-step cybersecurity investigation tools.

This module provides higher-level investigation flows that use the
read-only tools in agent_v2.tools.* to perform multi-step reasoning
about incidents and related IT tickets.

All operations here are READ-ONLY and do NOT modify the database.
"""

from typing import Any, Dict, List
from agent_v2.tools import incident_tools, ticket_tools, analytics_tools


def investigate_incident(incident_id: int) -> Dict[str, Any]:
    """
    Perform a multi-step investigation of a single incident.

    Steps:
      1. Retrieve the primary incident.
      2. Analyse its severity, category, status, and description.
      3. Find other incidents in the same category.
      4. Find incidents with the same severity and status (possible patterns).
      5. Retrieve ticket workload stats (to see related operational pressure).

    Returns:
        {
          "incident": { ... } or None,
          "related_incidents_same_category": [ ... ],
          "related_incidents_same_severity_status": [ ... ],
          "ticket_workload": { ... },
          "summary_insights": str,
          "activity_log": [ "Retrieved incident ...", ... ]
        }
    """
    activity_log: List[str] = []

    # Step 1: Retrieve primary incident
    incident = incident_tools.get_incident(incident_id)
    if not incident:
        activity_log.append(f"Incident {incident_id} not found.")
        return {
            "incident": None,
            "related_incidents_same_category": [],
            "related_incidents_same_severity_status": [],
            "ticket_workload": {},
            "summary_insights": f"No incident found with ID {incident_id}.",
            "activity_log": activity_log,
        }

    activity_log.append(f"Retrieved incident {incident_id}.")

    severity = incident.get("severity")
    category = incident.get("category")
    status = incident.get("status")

    # Step 2: Incidents in same category (excluding itself)
    related_same_category = []
    if category:
        all_same_category = incident_tools.search_incidents(category=category)
        related_same_category = [
            inc for inc in all_same_category if inc.get("incident_id") != incident_id
        ]
        activity_log.append(
            f"Found {len(related_same_category)} other incidents in category '{category}'."
        )
    else:
        activity_log.append("Incident has no category; skipping same-category search.")

    # Step 3: Incidents with same severity and status (excluding itself)
    related_same_sev_status = []
    if severity and status:
        all_same_sev_status = incident_tools.search_incidents(
            severity=severity, status=status
        )
        related_same_sev_status = [
            inc for inc in all_same_sev_status if inc.get("incident_id") != incident_id
        ]
        activity_log.append(
            f"Found {len(related_same_sev_status)} other incidents with severity "
            f"'{severity}' and status '{status}'."
        )
    else:
        activity_log.append(
            "Incident is missing severity or status; skipping same-severity/status search."
        )

    # Step 4: Ticket workload overview
    workload = analytics_tools.get_ticket_workload()
    activity_log.append("Retrieved IT ticket workload statistics.")

    # Step 5: Build a simple textual insight summary (no hidden chain-of-thought)
    summary_parts: List[str] = []

    summary_parts.append(
        f"Incident {incident_id} is a {severity or 'unknown-severity'} "
        f"incident in category '{category or 'Unknown'}' with status '{status or 'Unknown'}'."
    )

    if related_same_category:
        summary_parts.append(
            f"There are {len(related_same_category)} other incidents in the same category "
            f"('{category}'), which may indicate a recurring issue in this area."
        )
    else:
        summary_parts.append(
            f"No other incidents were found in the same category ('{category}')."
        )

    if related_same_sev_status:
        summary_parts.append(
            f"There are {len(related_same_sev_status)} other incidents with the same "
            f"severity ('{severity}') and status ('{status}')."
        )
    else:
        summary_parts.append(
            f"No other incidents share the same severity ('{severity}') "
            f"and status ('{status}')."
        )

    tickets_by_assignee = workload.get("tickets_by_assignee", {})
    open_by_assignee = workload.get("open_tickets_by_assignee", {})

    if tickets_by_assignee:
        busiest = max(tickets_by_assignee.items(), key=lambda x: x[1])
        summary_parts.append(
            f"Overall, IT support workload shows {sum(tickets_by_assignee.values())} tickets "
            f"assigned, with the heaviest load on {busiest[0]} ({busiest[1]} total tickets)."
        )

    if open_by_assignee:
        open_busiest = max(open_by_assignee.items(), key=lambda x: x[1])
        summary_parts.append(
            f"For open tickets specifically, {open_busiest[0]} currently holds the highest "
            f"number of open tickets ({open_busiest[1]})."
        )

    summary_insights = " ".join(summary_parts)

    activity_log.append("Analysed patterns and generated investigation summary.")
    activity_log.append("Investigation completed.")

    return {
        "incident": incident,
        "related_incidents_same_category": related_same_category,
        "related_incidents_same_severity_status": related_same_sev_status,
        "ticket_workload": workload,
        "summary_insights": summary_insights,
        "activity_log": activity_log,
    }
