# import sqlite3, pandas and the sentinel database path
import sqlite3
import pandas as pd
from configpath import SENTINEL_DB

# the exact columns of the monitored (Sentinel) system's audit table
AUDIT_COLUMNS = [
    "id", "user_id", "action", "resource", "method", "endpoint",
    "ip_address", "user_agent", "session_id", "status_code",
    "response_time_ms", "metadata", "created_at",
]


# create the audit_trail table with the Sentinel schema
def create_audit_trail_table(conn):
    cursor = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS audit_trail (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        action TEXT,
        resource TEXT,
        method TEXT,
        endpoint TEXT,
        ip_address TEXT,
        user_agent TEXT,
        session_id TEXT,
        status_code INTEGER,
        response_time_ms INTEGER,
        metadata TEXT,
        created_at TEXT
    )'''
    cursor.execute(sql)
    conn.commit()


# import (or refresh) the audit trail from the external monitored system
def import_sentinel_audit(conn):
    src = sqlite3.connect(SENTINEL_DB)
    try:
        data = pd.read_sql_query("SELECT * FROM audit_trails", src)
    finally:
        src.close()
    create_audit_trail_table(conn)
    data.to_sql('audit_trail', conn, if_exists='replace', index=False)
    return len(data)


# a function to get all audit trail events
def get_all_audit_trail(conn):
    sql = 'SELECT * FROM audit_trail'
    data = pd.read_sql(sql, conn)
    return data


# get the next window of audit events starting after the given id
def get_audit_window(conn, after_id, limit=100):
    sql = """
        SELECT * FROM audit_trail
        WHERE id > ?
        ORDER BY id ASC
        LIMIT ?
    """
    return pd.read_sql_query(sql, conn, params=(after_id, limit))


# the first audit event id
def get_min_audit_id(conn):
    return conn.execute("SELECT MIN(id) FROM audit_trail").fetchone()[0]


# the last audit event id
def get_max_audit_id(conn):
    return conn.execute("SELECT MAX(id) FROM audit_trail").fetchone()[0]
