# agent_v2/tools/incident_tools.py

"""
Read-only tools for working with cyber_incidents data.

These functions are designed to be safe, simple building blocks that
an AI agent can call. They use the existing SQLite database via
app_model.db.get_connection and never modify data.
"""

from typing import List, Dict, Optional, Any
from app_model.db import get_connection
import sqlite3


def _row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a SQLite row to a plain dict using column names."""
    return {description[0]: value for description, value in zip(cursor.description, row)}


def search_incidents(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search cyber_incidents with optional filters.

    Parameters:
        severity: Optional severity filter ("Low", "Medium", "High", "Critical").
        status: Optional status filter ("Open", "Resolved", "Closed").
        category: Optional category filter (e.g. "Malware", "Phishing").

    Returns:
        A list of dictionaries, one per incident, keys match table columns.

    On any error, returns an empty list.
    """
    query = "SELECT * FROM cyber_incidents WHERE 1=1"
    params: list = []

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if status:
        query += " AND status = ?"
        params.append(status)

    if category:
        query += " AND category = ?"
        params.append(category)

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_dict(cursor, row) for row in rows]
    except Exception:
        return []


def get_incident(incident_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single incident by its incident_id.

    Returns:
        A dict or None if not found or on error.
    """
    query = "SELECT * FROM cyber_incidents WHERE incident_id = ?"

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, (incident_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(cursor, row)
    except Exception:
        return None


def get_incident_statistics() -> Dict[str, Any]:
    """
    Compute basic statistics over cyber_incidents.

    Returns:
        {
            "total_incidents",
            "open_incidents",
            "resolved_incidents",
            "closed_incidents",
            "critical_incidents",
            "high_incidents",
            "medium_incidents",
            "low_incidents",
        }

    On error, returns all counts as 0.
    """
    stats = {
        "total_incidents": 0,
        "open_incidents": 0,
        "resolved_incidents": 0,
        "closed_incidents": 0,
        "critical_incidents": 0,
        "high_incidents": 0,
        "medium_incidents": 0,
        "low_incidents": 0,
    }

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Total incidents
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
        stats["total_incidents"] = cursor.fetchone()[0] or 0

        # Status counts
        cursor.execute(
            "SELECT status, COUNT(*) FROM cyber_incidents GROUP BY status"
        )
        for status, count in cursor.fetchall():
            if status == "Open":
                stats["open_incidents"] = count
            elif status == "Resolved":
                stats["resolved_incidents"] = count
            elif status == "Closed":
                stats["closed_incidents"] = count

        # Severity counts
        cursor.execute(
            "SELECT severity, COUNT(*) FROM cyber_incidents GROUP BY severity"
        )
        for severity, count in cursor.fetchall():
            if severity == "Critical":
                stats["critical_incidents"] = count
            elif severity == "High":
                stats["high_incidents"] = count
            elif severity == "Medium":
                stats["medium_incidents"] = count
            elif severity == "Low":
                stats["low_incidents"] = count

    except Exception:
        pass

    return stats
