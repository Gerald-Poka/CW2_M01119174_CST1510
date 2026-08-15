# agent_v2/tools/ticket_tools.py

"""
Read-only tools for working with it_tickets data.
"""

from typing import List, Dict, Optional, Any
from app_model.db import get_connection
import sqlite3


def _row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    return {description[0]: value for description, value in zip(cursor.description, row)}


def search_tickets(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search it_tickets with optional filters.

    Parameters:
        priority: "High", "Medium", "Low".
        status: "Open", "Resolved", "Closed".
        assigned_to: e.g. "IT_Support_A".

    Returns:
        List of ticket dicts. Empty list on error.
    """
    query = "SELECT * FROM it_tickets WHERE 1=1"
    params: list = []

    if priority:
        query += " AND priority = ?"
        params.append(priority)

    if status:
        query += " AND status = ?"
        params.append(status)

    if assigned_to:
        query += " AND assigned_to = ?"
        params.append(assigned_to)

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_dict(cursor, row) for row in rows]
    except Exception:
        return []


def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single IT ticket by ticket_id.
    """
    query = "SELECT * FROM it_tickets WHERE ticket_id = ?"

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, (ticket_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(cursor, row)
    except Exception:
        return None


def get_ticket_statistics() -> Dict[str, Any]:
    """
    Compute basic statistics over IT tickets.

    Returns:
        {
            "total_tickets",
            "open_tickets",
            "resolved_tickets",
            "closed_tickets",
            "high_priority",
            "medium_priority",
            "low_priority",
            "average_resolution_time": float or None
        }
    """
    stats = {
        "total_tickets": 0,
        "open_tickets": 0,
        "resolved_tickets": 0,
        "closed_tickets": 0,
        "high_priority": 0,
        "medium_priority": 0,
        "low_priority": 0,
        "average_resolution_time": None,
    }

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Total tickets
        cursor.execute("SELECT COUNT(*) FROM it_tickets")
        stats["total_tickets"] = cursor.fetchone()[0] or 0

        # Status counts
        cursor.execute("SELECT status, COUNT(*) FROM it_tickets GROUP BY status")
        for status, count in cursor.fetchall():
            if status == "Open":
                stats["open_tickets"] = count
            elif status == "Resolved":
                stats["resolved_tickets"] = count
            elif status == "Closed":
                stats["closed_tickets"] = count

        # Priority counts
        cursor.execute("SELECT priority, COUNT(*) FROM it_tickets GROUP BY priority")
        for priority, count in cursor.fetchall():
            if priority == "High":
                stats["high_priority"] = count
            elif priority == "Medium":
                stats["medium_priority"] = count
            elif priority == "Low":
                stats["low_priority"] = count

        # Average resolution time (for rows where resolution_time is not null)
        cursor.execute(
            """
            SELECT AVG(resolution_time)
            FROM it_tickets
            WHERE resolution_time IS NOT NULL
            """
        )
        avg = cursor.fetchone()[0]
        stats["average_resolution_time"] = float(avg) if avg is not None else None

    except Exception:
        pass

    return stats
