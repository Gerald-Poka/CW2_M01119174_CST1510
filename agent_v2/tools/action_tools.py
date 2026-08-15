# agent_v2/tools/action_tools.py

"""
Controlled write/action tools for incidents and IT tickets.

These functions perform actual database modifications using the existing
SQLite database (via app_model.db.get_connection).

SECURITY MODEL:
- These functions SHOULD NOT be called directly by the LLM.
- The Cyber Intelligence Agent should first create a 'pending action'
  in agent_v2.memory, and the Streamlit UI must require explicit user
  confirmation before executing any of these functions.

All SQL is parameterised and uses the existing DB schema.
"""

from typing import Optional, Dict, Any
from app_model.db import get_connection
import sqlite3
from datetime import datetime


# ---- INCIDENT ACTIONS ----

def create_incident(
    timestamp: Optional[str],
    severity: str,
    category: str,
    status: str,
    description: str,
) -> int:
    """
    Create a new cyber incident.

    Parameters:
        timestamp: ISO datetime string or None. If None, current time is used.
        severity: One of "Low", "Medium", "High", "Critical".
        category: Incident category (e.g. "Malware", "Phishing").
        status: One of "Open", "Resolved", "Closed".
        description: Text description.

    Returns:
        The new incident_id.

    Uses the same ID pattern as add_cyber_incident: starting at 1000.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Find current max incident_id
    cursor.execute("SELECT MAX(incident_id) FROM cyber_incidents")
    result = cursor.fetchone()[0]
    incident_id = 1000 if result is None else result + 1

    cursor.execute(
        """
        INSERT INTO cyber_incidents
        (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (incident_id, timestamp, severity, category, status, description),
    )

    conn.commit()
    return incident_id


def update_incident(
    incident_id: int,
    updates: Dict[str, Any],
) -> bool:
    """
    Update fields on an existing incident.

    Parameters:
        incident_id: The ID of the incident to update.
        updates: Dict of column -> new value, e.g. {"status": "Resolved"}.

    Returns:
        True if at least one row was updated, False otherwise.

    Only allows updates to known columns.
    """
    allowed_fields = {"timestamp", "severity", "category", "status", "description"}
    set_clauses = []
    params = []

    for field, value in updates.items():
        if field not in allowed_fields:
            # Ignore unsupported fields
            continue
        set_clauses.append(f"{field} = ?")
        params.append(value)

    if not set_clauses:
        # nothing to update
        return False

    params.append(incident_id)

    query = f"""
        UPDATE cyber_incidents
        SET {', '.join(set_clauses)}
        WHERE incident_id = ?
    """

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

    return cursor.rowcount > 0


def close_incident(incident_id: int) -> bool:
    """
    Convenience function to set an incident's status to 'Closed'.

    Returns:
        True if the incident was updated, False otherwise.
    """
    return update_incident(incident_id, {"status": "Closed"})


# ---- IT TICKET ACTIONS ----

def create_ticket(
    priority: str,
    description: str,
    status: str,
    assigned_to: str,
    created_at: Optional[str] = None,
    resolution_time: Optional[float] = None,
) -> int:
    """
    Create a new IT ticket.

    Parameters:
        priority: "High", "Medium", "Low".
        description: Ticket description.
        status: "Open", "Resolved", "Closed".
        assigned_to: e.g. "IT_Support_A".
        created_at: Optional ISO datetime string. If None, current time used.
        resolution_time: Optional number of hours to resolve (float).

    Returns:
        The new ticket_id.

    Uses the same ID pattern as app_model.it_tickets.add_it_ticket:
    start at 2000.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if not created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Find current max ticket_id
    cursor.execute("SELECT MAX(ticket_id) FROM it_tickets")
    result = cursor.fetchone()[0]
    ticket_id = 2000 if result is None else result + 1

    cursor.execute(
        """
        INSERT INTO it_tickets
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (ticket_id, priority, description, status, assigned_to, created_at, resolution_time),
    )

    conn.commit()
    return ticket_id


def update_ticket(
    ticket_id: int,
    updates: Dict[str, Any],
) -> bool:
    """
    Update fields on an existing IT ticket.

    Parameters:
        ticket_id: The ID of the ticket to update.
        updates: Dict of column -> new value, e.g. {"status": "Resolved"}.

    Returns:
        True if at least one row was updated, False otherwise.

    Only allows updates to known columns.
    """
    allowed_fields = {
        "priority",
        "description",
        "status",
        "assigned_to",
        "created_at",
        "resolution_time",
    }
    set_clauses = []
    params = []

    for field, value in updates.items():
        if field not in allowed_fields:
            continue
        set_clauses.append(f"{field} = ?")
        params.append(value)

    if not set_clauses:
        return False

    params.append(ticket_id)

    query = f"""
        UPDATE it_tickets
        SET {', '.join(set_clauses)}
        WHERE ticket_id = ?
    """

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

    return cursor.rowcount > 0


def assign_ticket(ticket_id: int, assignee: str) -> bool:
    """
    Assign a ticket to a specific support engineer.
    """
    return update_ticket(ticket_id, {"assigned_to": assignee})


def close_ticket(ticket_id: int) -> bool:
    """
    Convenience function to set a ticket's status to 'Closed'.

    Returns:
        True if the ticket was updated, False otherwise.
    """
    return update_ticket(ticket_id, {"status": "Closed"})
