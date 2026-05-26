
"""
Error Notification System

This module records and summarizes system errors.

It does not send external emails yet.
It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from datetime import datetime
import traceback
import pandas as pd

from trading_database import (
    initialize_trading_database,
    get_database_connection,
    safe_json
)


VALID_SEVERITIES = [
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


def initialize_error_tables():
    """
    Create error notification tables.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            severity TEXT NOT NULL,
            component TEXT,
            error_type TEXT,
            error_message TEXT,
            resolved INTEGER DEFAULT 0,
            resolved_at TEXT,
            resolution_note TEXT,
            raw_error_json TEXT
        )
    """)

    conn.commit()
    conn.close()

    return True


def normalize_severity(severity):
    severity = str(severity or "ERROR").upper().strip()

    if severity not in VALID_SEVERITIES:
        severity = "ERROR"

    return severity


def notify_error(
    component,
    error,
    severity="ERROR",
    context=None,
    resolved=False
):
    """
    Record an error notification.

    error may be:
    - Exception object
    - string
    - dictionary
    """

    initialize_error_tables()

    severity = normalize_severity(severity)

    error_type = ""
    error_message = ""
    traceback_text = ""

    if isinstance(error, Exception):
        error_type = type(error).__name__
        error_message = str(error)
        traceback_text = traceback.format_exc()
    elif isinstance(error, dict):
        error_type = str(error.get("error_type", "Error"))
        error_message = str(error.get("error_message", error))
        traceback_text = str(error.get("traceback", ""))
    else:
        error_type = "Message"
        error_message = str(error)

    payload = {
        "component": component,
        "severity": severity,
        "error_type": error_type,
        "error_message": error_message,
        "traceback": traceback_text,
        "context": context or {},
        "resolved": bool(resolved),
    }

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO error_notifications (
            created_at,
            severity,
            component,
            error_type,
            error_message,
            resolved,
            resolved_at,
            resolution_note,
            raw_error_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            severity,
            component,
            error_type,
            error_message,
            1 if resolved else 0,
            now if resolved else None,
            "Recorded as resolved on creation." if resolved else None,
            safe_json(payload),
        )
    )

    error_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "recorded": True,
        "error_id": error_id,
        "created_at": now,
        "severity": severity,
        "component": component,
        "error_type": error_type,
        "error_message": error_message,
    }


def notify_message(component, message, severity="INFO", context=None):
    """
    Record a non-exception notification message.
    """

    return notify_error(
        component=component,
        error=str(message),
        severity=severity,
        context=context or {},
        resolved=severity.upper() in ["INFO"]
    )


def read_error_notifications(limit=100, unresolved_only=False, severity=None):
    """
    Read recent error notifications.
    """

    initialize_error_tables()

    conn = get_database_connection()

    query = """
        SELECT *
        FROM error_notifications
    """

    conditions = []
    params = []

    if unresolved_only:
        conditions.append("resolved = 0")

    if severity:
        conditions.append("severity = ?")
        params.append(normalize_severity(severity))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(int(limit))

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


def mark_error_resolved(error_id, resolution_note="Resolved."):
    """
    Mark an error notification as resolved.
    """

    initialize_error_tables()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE error_notifications
        SET resolved = 1,
            resolved_at = ?,
            resolution_note = ?
        WHERE id = ?
        """,
        (
            now,
            resolution_note,
            int(error_id),
        )
    )

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    return {
        "updated": updated > 0,
        "error_id": error_id,
        "resolved_at": now,
        "resolution_note": resolution_note,
    }


def summarize_errors(limit=1000):
    """
    Summarize recent errors.
    """

    df = read_error_notifications(limit=limit)

    if df.empty:
        return {
            "has_data": False,
            "total_errors": 0,
            "unresolved_errors": 0,
            "critical_errors": 0,
            "message": "No error notifications found.",
        }

    total_errors = len(df)
    unresolved_errors = len(df[df["resolved"] == 0])
    critical_errors = len(df[df["severity"] == "CRITICAL"])

    severity_counts = df["severity"].value_counts().to_dict()
    component_counts = df["component"].value_counts().to_dict()

    return {
        "has_data": True,
        "total_errors": int(total_errors),
        "unresolved_errors": int(unresolved_errors),
        "critical_errors": int(critical_errors),
        "severity_counts": severity_counts,
        "component_counts": component_counts,
    }


def get_error_notifier_status():
    """
    Return error notifier status.
    """

    initialize_error_tables()
    summary = summarize_errors(limit=100000)

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "valid_severities": VALID_SEVERITIES,
        "purpose": "Centralized error logging and dashboard review.",
    }
