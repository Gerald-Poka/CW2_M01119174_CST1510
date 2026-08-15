# agent_v2/tools/analytics_tools.py

"""
Higher-level analytics tools that summarise incidents, tickets,
and datasets. These are read-only and intended for use by the
Cyber Intelligence Agent.
"""

from typing import Dict, Any
from app_model.db import get_connection
import sqlite3


def get_dashboard_summary() -> Dict[str, Any]:
    """
    Return a compact dashboard summary combining key metrics.

    Returns:
        {
            "total_incidents",
            "critical_incidents",
            "high_incidents",
            "open_incidents",
            "total_tickets",
            "open_tickets",
            "high_priority_tickets",
            "total_datasets",
        }

    On error, returns zeros.
    """
    summary = {
        "total_incidents": 0,
        "critical_incidents": 0,
        "high_incidents": 0,
        "open_incidents": 0,
        "total_tickets": 0,
        "open_tickets": 0,
        "high_priority_tickets": 0,
        "total_datasets": 0,
    }

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Incident stats
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
        summary["total_incidents"] = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM cyber_incidents WHERE severity = 'Critical'"
        )
        summary["critical_incidents"] = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM cyber_incidents WHERE severity = 'High'"
        )
        summary["high_incidents"] = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM cyber_incidents WHERE status = 'Open'"
        )
        summary["open_incidents"] = cursor.fetchone()[0] or 0

        # Ticket stats
        cursor.execute("SELECT COUNT(*) FROM it_tickets")
        summary["total_tickets"] = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM it_tickets WHERE status = 'Open'")
        summary["open_tickets"] = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT COUNT(*) FROM it_tickets WHERE priority = 'High'"
        )
        summary["high_priority_tickets"] = cursor.fetchone()[0] or 0

        # Dataset stats
        cursor.execute("SELECT COUNT(*) FROM datasets_metadata")
        summary["total_datasets"] = cursor.fetchone()[0] or 0

    except Exception:
        pass

    return summary


def get_incident_category_statistics() -> Dict[str, int]:
    """
    Return a count of incidents per category.

    Returns:
        {category_name: count, ...}
        Empty dict on error.
    """
    stats: Dict[str, int] = {}

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category, COUNT(*) FROM cyber_incidents GROUP BY category"
        )
        for category, count in cursor.fetchall():
            stats[category] = count
    except Exception:
        pass

    return stats


def get_ticket_workload() -> Dict[str, Any]:
    """
    Return simple workload statistics for IT support:

    Returns:
        {
            "tickets_by_assignee": { "IT_Support_A": n, ... },
            "open_tickets_by_assignee": { "IT_Support_A": n, ... }
        }

        Empty dicts on error.
    """
    workload = {
        "tickets_by_assignee": {},
        "open_tickets_by_assignee": {},
    }

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # All tickets by assignee
        cursor.execute(
            "SELECT assigned_to, COUNT(*) FROM it_tickets GROUP BY assigned_to"
        )
        for assigned_to, count in cursor.fetchall():
            workload["tickets_by_assignee"][assigned_to] = count

        # Open tickets by assignee
        cursor.execute(
            """
            SELECT assigned_to, COUNT(*)
            FROM it_tickets
            WHERE status = 'Open'
            GROUP BY assigned_to
            """
        )
        for assigned_to, count in cursor.fetchall():
            workload["open_tickets_by_assignee"][assigned_to] = count

    except Exception:
        pass

    return workload
