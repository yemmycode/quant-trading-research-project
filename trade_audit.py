
"""
Trade Audit Logger

This module records important trading workflow events.

It is used for:
- signal review
- risk checks
- manual confirmations
- broker order attempts
- broker responses
- errors

The audit log is saved locally as CSV for now.
Later, it can be moved into SQLite or a cloud database.
"""

from pathlib import Path
from datetime import datetime
import json
import pandas as pd


PROJECT_PATH = Path(__file__).resolve().parent
LOGS_PATH = PROJECT_PATH / "logs"
AUDIT_FILE = LOGS_PATH / "trade_audit_log.csv"


def ensure_logs_folder():
    """
    Ensure logs folder exists.
    """

    LOGS_PATH.mkdir(parents=True, exist_ok=True)


def safe_json(value):
    """
    Convert dict/list objects into JSON strings for CSV storage.
    """

    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


def create_audit_event(
    event_type,
    ticker=None,
    side=None,
    quantity=None,
    order_type=None,
    limit_price=None,
    strategy_name=None,
    signal=None,
    risk_approved=None,
    risk_reason=None,
    manual_confirmation=False,
    broker_name=None,
    execution_mode=None,
    order_id=None,
    broker_status=None,
    message=None,
    details=None,
    error=None
):
    """
    Create a structured audit event dictionary.
    """

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "ticker": ticker,
        "side": side,
        "quantity": quantity,
        "order_type": order_type,
        "limit_price": limit_price,
        "strategy_name": strategy_name,
        "signal": signal,
        "risk_approved": risk_approved,
        "risk_reason": risk_reason,
        "manual_confirmation": manual_confirmation,
        "broker_name": broker_name,
        "execution_mode": execution_mode,
        "order_id": order_id,
        "broker_status": broker_status,
        "message": message,
        "details": safe_json(details or {}),
        "error": str(error) if error else ""
    }


def append_audit_event(event):
    """
    Append one event to the audit CSV log.
    """

    ensure_logs_folder()

    event_df = pd.DataFrame([event])

    if AUDIT_FILE.exists():
        existing_df = pd.read_csv(AUDIT_FILE)
        updated_df = pd.concat([existing_df, event_df], ignore_index=True)
    else:
        updated_df = event_df

    updated_df.to_csv(AUDIT_FILE, index=False)

    return AUDIT_FILE


def log_audit_event(**kwargs):
    """
    Create and append audit event in one call.
    """

    event = create_audit_event(**kwargs)
    audit_file = append_audit_event(event)

    return {
        "event": event,
        "audit_file": str(audit_file)
    }


def read_audit_log(limit=100):
    """
    Read latest audit log records.
    """

    ensure_logs_folder()

    if not AUDIT_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(AUDIT_FILE)

    if df.empty:
        return df

    return df.tail(limit)


def clear_audit_log():
    """
    Clear audit log.

    Use carefully for development/testing only.
    """

    ensure_logs_folder()

    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()

    return True
