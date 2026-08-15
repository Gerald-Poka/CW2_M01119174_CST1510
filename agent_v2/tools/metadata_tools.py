# agent_v2/tools/metadata_tools.py

"""
Read-only tools for working with datasets_metadata.
"""

from typing import List, Dict, Optional, Any
from app_model.db import get_connection
import sqlite3


def _row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> Dict[str, Any]:
    return {description[0]: value for description, value in zip(cursor.description, row)}


def search_datasets(uploaded_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search datasets_metadata with optional uploaded_by filter.

    Parameters:
        uploaded_by: e.g. "data_scientist", "cyber_admin".

    Returns:
        List of dataset metadata dicts. Empty list on error.
    """
    query = "SELECT * FROM datasets_metadata WHERE 1=1"
    params: list = []

    if uploaded_by:
        query += " AND uploaded_by = ?"
        params.append(uploaded_by)

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_dict(cursor, row) for row in rows]
    except Exception:
        return []


def get_dataset(dataset_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single dataset metadata record by dataset_id.
    """
    query = "SELECT * FROM datasets_metadata WHERE dataset_id = ?"

    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, (dataset_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(cursor, row)
    except Exception:
        return None
