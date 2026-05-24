
"""
Unified Order State Manager

This module manages the lifecycle state of proposed and broker-submitted orders.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from pathlib import Path
from datetime import datetime
import sqlite3
import json
import pandas as pd

from trading_database import (
    initialize_trading_database,
    get_database_connection,
    safe_json
)


VALID_ORDER_STATES = [
    "proposed",
    "risk_checked",
    "approved",
    "blocked",
    "submitted",
    "acknowledged",
    "filled",
    "partially_filled",
    "cancel_requested",
    "cancelled",
    "rejected",
    "failed",
    "expired",
]


TERMINAL_ORDER_STATES = [
    "filled",
    "cancelled",
    "rejected",
    "failed",
    "expired",
]


def initialize_order_state_tables():
    """
    Create order state tracking tables.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_state_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            order_key TEXT NOT NULL,
            proposal_id INTEGER,
            broker_order_row_id INTEGER,
            broker_order_id TEXT,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            previous_state TEXT,
            new_state TEXT NOT NULL,
            event_type TEXT,
            message TEXT,
            raw_event_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_current_state (
            order_key TEXT PRIMARY KEY,
            updated_at TEXT NOT NULL,
            proposal_id INTEGER,
            broker_order_row_id INTEGER,
            broker_order_id TEXT,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            current_state TEXT NOT NULL,
            is_terminal INTEGER NOT NULL,
            last_message TEXT,
            raw_state_json TEXT
        )
    """)

    conn.commit()
    conn.close()

    return True


def normalize_order_state(state):
    """
    Validate and normalize order state.
    """

    if state is None:
        raise ValueError("Order state cannot be None.")

    state = str(state).strip().lower()

    if state not in VALID_ORDER_STATES:
        raise ValueError(
            f"Unsupported order state: {state}. Valid states: {VALID_ORDER_STATES}"
        )

    return state


def generate_order_key(
    proposal_id=None,
    broker_order_id=None,
    ticker=None,
    side=None,
    created_at=None
):
    """
    Generate a stable order key.
    """

    if broker_order_id:
        return f"broker:{broker_order_id}"

    if proposal_id:
        return f"proposal:{proposal_id}"

    ticker = str(ticker or "UNKNOWN").upper()
    side = str(side or "UNKNOWN").upper()
    timestamp = created_at or datetime.now().strftime("%Y%m%d%H%M%S")

    return f"manual:{ticker}:{side}:{timestamp}"


def get_current_order_state(order_key):
    """
    Get latest current state for an order.
    """

    initialize_order_state_tables()

    conn = get_database_connection()

    query = """
        SELECT *
        FROM order_current_state
        WHERE order_key = ?
    """

    df = pd.read_sql_query(query, conn, params=(order_key,))
    conn.close()

    if df.empty:
        return None

    return df.iloc[0].to_dict()


def record_order_state_event(
    new_state,
    order_key=None,
    proposal_id=None,
    broker_order_row_id=None,
    broker_order_id=None,
    ticker=None,
    side=None,
    quantity=None,
    event_type="ORDER_STATE_UPDATE",
    message="",
    details=None
):
    """
    Record an order state transition and update current state.
    """

    initialize_order_state_tables()

    new_state = normalize_order_state(new_state)

    if order_key is None:
        order_key = generate_order_key(
            proposal_id=proposal_id,
            broker_order_id=broker_order_id,
            ticker=ticker,
            side=side
        )

    existing_state = get_current_order_state(order_key)
    previous_state = existing_state.get("current_state") if existing_state else None

    if previous_state in TERMINAL_ORDER_STATES:
        return {
            "recorded": False,
            "order_key": order_key,
            "previous_state": previous_state,
            "new_state": new_state,
            "reason": f"Order is already terminal: {previous_state}. State update blocked."
        }

    is_terminal = 1 if new_state in TERMINAL_ORDER_STATES else 0

    event_payload = {
        "order_key": order_key,
        "proposal_id": proposal_id,
        "broker_order_row_id": broker_order_row_id,
        "broker_order_id": broker_order_id,
        "ticker": ticker,
        "side": side,
        "quantity": quantity,
        "previous_state": previous_state,
        "new_state": new_state,
        "event_type": event_type,
        "message": message,
        "details": details or {},
    }

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO order_state_events (
            created_at,
            order_key,
            proposal_id,
            broker_order_row_id,
            broker_order_id,
            ticker,
            side,
            quantity,
            previous_state,
            new_state,
            event_type,
            message,
            raw_event_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            order_key,
            proposal_id,
            broker_order_row_id,
            broker_order_id,
            ticker,
            side,
            quantity,
            previous_state,
            new_state,
            event_type,
            message,
            safe_json(event_payload),
        )
    )

    cursor.execute(
        """
        INSERT INTO order_current_state (
            order_key,
            updated_at,
            proposal_id,
            broker_order_row_id,
            broker_order_id,
            ticker,
            side,
            quantity,
            current_state,
            is_terminal,
            last_message,
            raw_state_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(order_key) DO UPDATE SET
            updated_at = excluded.updated_at,
            proposal_id = excluded.proposal_id,
            broker_order_row_id = excluded.broker_order_row_id,
            broker_order_id = excluded.broker_order_id,
            ticker = excluded.ticker,
            side = excluded.side,
            quantity = excluded.quantity,
            current_state = excluded.current_state,
            is_terminal = excluded.is_terminal,
            last_message = excluded.last_message,
            raw_state_json = excluded.raw_state_json
        """,
        (
            order_key,
            now,
            proposal_id,
            broker_order_row_id,
            broker_order_id,
            ticker,
            side,
            quantity,
            new_state,
            is_terminal,
            message,
            safe_json(event_payload),
        )
    )

    conn.commit()
    conn.close()

    return {
        "recorded": True,
        "order_key": order_key,
        "previous_state": previous_state,
        "new_state": new_state,
        "is_terminal": bool(is_terminal),
        "message": message,
    }


def create_order_state_from_proposal(proposal, proposal_id=None):
    """
    Create initial proposed state from an order proposal dictionary.
    """

    order_key = generate_order_key(
        proposal_id=proposal_id,
        ticker=proposal.get("ticker"),
        side=proposal.get("side")
    )

    return record_order_state_event(
        order_key=order_key,
        proposal_id=proposal_id,
        ticker=proposal.get("ticker"),
        side=proposal.get("side"),
        quantity=proposal.get("quantity"),
        new_state="proposed" if proposal.get("actionable") else "blocked",
        event_type="ORDER_PROPOSAL_STATE_CREATED",
        message=proposal.get("reason", "Order proposal state created."),
        details=proposal
    )


def record_risk_check_state(
    order_key,
    risk_approved,
    risk_reason,
    details=None
):
    """
    Record state after risk check.
    """

    if risk_approved:
        new_state = "approved"
        event_type = "ORDER_RISK_APPROVED"
    else:
        new_state = "blocked"
        event_type = "ORDER_RISK_BLOCKED"

    return record_order_state_event(
        order_key=order_key,
        new_state=new_state,
        event_type=event_type,
        message=risk_reason,
        details=details or {}
    )


def record_broker_submission_state(
    order_key,
    broker_response,
    broker_order_row_id=None
):
    """
    Record submitted state after broker submission.
    """

    broker_status = (
        broker_response.get("order_status")
        or broker_response.get("broker_status")
        or "submitted"
    )

    broker_order_id = (
        broker_response.get("order_id")
        or broker_response.get("broker_order_id")
    )

    return record_order_state_event(
        order_key=order_key,
        broker_order_row_id=broker_order_row_id,
        broker_order_id=broker_order_id,
        ticker=broker_response.get("ticker"),
        side=broker_response.get("side"),
        quantity=broker_response.get("quantity"),
        new_state="submitted",
        event_type="ORDER_SUBMITTED_TO_BROKER",
        message=f"Order submitted to broker with status: {broker_status}",
        details=broker_response
    )


def record_broker_status_update(
    order_key,
    broker_status,
    message=None,
    details=None
):
    """
    Map broker status to internal order state and record it.
    """

    broker_status_clean = str(broker_status or "").strip().lower()

    status_map = {
        "submitted": "submitted",
        "presubmitted": "submitted",
        "pending_submit": "submitted",
        "api_pending": "submitted",
        "filled": "filled",
        "partial": "partially_filled",
        "partially_filled": "partially_filled",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "inactive": "rejected",
        "rejected": "rejected",
        "failed": "failed",
        "expired": "expired",
    }

    new_state = status_map.get(broker_status_clean, "acknowledged")

    return record_order_state_event(
        order_key=order_key,
        new_state=new_state,
        event_type="BROKER_STATUS_UPDATE",
        message=message or f"Broker status update: {broker_status}",
        details=details or {"broker_status": broker_status}
    )


def read_order_current_states(limit=100):
    """
    Read latest current order states.
    """

    initialize_order_state_tables()

    conn = get_database_connection()

    query = """
        SELECT *
        FROM order_current_state
        ORDER BY updated_at DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=(int(limit),))
    conn.close()

    return df


def read_order_state_events(order_key=None, limit=100):
    """
    Read order state event history.
    """

    initialize_order_state_tables()

    conn = get_database_connection()

    if order_key:
        query = """
            SELECT *
            FROM order_state_events
            WHERE order_key = ?
            ORDER BY id DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(order_key, int(limit)))
    else:
        query = """
            SELECT *
            FROM order_state_events
            ORDER BY id DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(int(limit),))

    conn.close()

    return df


def get_order_state_manager_status():
    """
    Return order state manager table status.
    """

    initialize_order_state_tables()

    current_df = read_order_current_states(limit=100000)
    events_df = read_order_state_events(limit=100000)

    return {
        "current_orders": len(current_df),
        "state_events": len(events_df),
        "valid_states": VALID_ORDER_STATES,
        "terminal_states": TERMINAL_ORDER_STATES,
    }
