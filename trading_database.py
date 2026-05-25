
"""
SQLite Trading Database Foundation

This module creates and manages a local SQLite database for the trading system.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from pathlib import Path
from datetime import datetime
import sqlite3
import json
import pandas as pd


PROJECT_PATH = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_PATH / "database"
DATABASE_FILE = DATABASE_PATH / "trading_system.db"


def ensure_database_folder():
    DATABASE_PATH.mkdir(parents=True, exist_ok=True)


def get_database_connection():
    """
    Return a SQLite database connection.
    """

    ensure_database_folder()
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def safe_json(value):
    """
    Convert a value to JSON string safely.
    """

    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


def initialize_trading_database():
    """
    Create all required trading database tables.
    """

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            ticker TEXT,
            strategy_name TEXT,
            action TEXT,
            reason TEXT,
            latest_price REAL,
            latest_date TEXT,
            raw_signal_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            signal_id INTEGER,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            order_type TEXT,
            limit_price REAL,
            estimated_order_value REAL,
            proposal_status TEXT,
            actionable INTEGER,
            raw_proposal_json TEXT,
            FOREIGN KEY(signal_id) REFERENCES signals(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            proposal_id INTEGER,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            approved INTEGER,
            reason TEXT,
            raw_risk_json TEXT,
            FOREIGN KEY(proposal_id) REFERENCES order_proposals(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS broker_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            proposal_id INTEGER,
            risk_check_id INTEGER,
            broker_name TEXT,
            execution_mode TEXT,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            order_type TEXT,
            limit_price REAL,
            broker_order_id TEXT,
            broker_status TEXT,
            submitted_to_broker INTEGER,
            raw_broker_response_json TEXT,
            FOREIGN KEY(proposal_id) REFERENCES order_proposals(id),
            FOREIGN KEY(risk_check_id) REFERENCES risk_checks(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            event_type TEXT,
            ticker TEXT,
            message TEXT,
            severity TEXT,
            raw_event_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            event_type TEXT,
            component TEXT,
            status TEXT,
            message TEXT,
            raw_event_json TEXT
        )
    """)

    conn.commit()
    conn.close()

    return str(DATABASE_FILE)


def insert_signal(signal_result):
    """
    Insert a generated signal into the database.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO signals (
            created_at,
            ticker,
            strategy_name,
            action,
            reason,
            latest_price,
            latest_date,
            raw_signal_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            signal_result.get("ticker"),
            signal_result.get("strategy_label") or signal_result.get("strategy_name"),
            signal_result.get("action"),
            signal_result.get("reason"),
            signal_result.get("latest_close"),
            signal_result.get("latest_date"),
            safe_json(signal_result),
        )
    )

    signal_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return signal_id


def insert_order_proposal(proposal, signal_id=None):
    """
    Insert an order proposal into the database.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO order_proposals (
            created_at,
            signal_id,
            ticker,
            side,
            quantity,
            order_type,
            limit_price,
            estimated_order_value,
            proposal_status,
            actionable,
            raw_proposal_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            signal_id,
            proposal.get("ticker"),
            proposal.get("side"),
            proposal.get("quantity"),
            proposal.get("order_type"),
            proposal.get("limit_price"),
            proposal.get("estimated_order_value"),
            proposal.get("proposal_status"),
            1 if proposal.get("actionable") else 0,
            safe_json(proposal),
        )
    )

    proposal_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return proposal_id


def insert_risk_check(risk_result, proposal_id=None, ticker=None, side=None, quantity=None):
    """
    Insert a risk check result into the database.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO risk_checks (
            created_at,
            proposal_id,
            ticker,
            side,
            quantity,
            approved,
            reason,
            raw_risk_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            proposal_id,
            ticker,
            side,
            quantity,
            1 if getattr(risk_result, "approved", False) else 0,
            getattr(risk_result, "reason", ""),
            safe_json({
                "approved": getattr(risk_result, "approved", False),
                "reason": getattr(risk_result, "reason", ""),
                "details": getattr(risk_result, "details", {}),
            }),
        )
    )

    risk_check_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return risk_check_id


def insert_broker_order(
    broker_response,
    proposal_id=None,
    risk_check_id=None,
    submitted_to_broker=False
):
    """
    Insert broker order result into the database.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO broker_orders (
            created_at,
            proposal_id,
            risk_check_id,
            broker_name,
            execution_mode,
            ticker,
            side,
            quantity,
            order_type,
            limit_price,
            broker_order_id,
            broker_status,
            submitted_to_broker,
            raw_broker_response_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            proposal_id,
            risk_check_id,
            broker_response.get("broker_name", "ibkr"),
            broker_response.get("execution_mode"),
            broker_response.get("ticker"),
            broker_response.get("side"),
            broker_response.get("quantity"),
            broker_response.get("order_type"),
            broker_response.get("limit_price"),
            broker_response.get("order_id") or broker_response.get("broker_order_id"),
            broker_response.get("order_status") or broker_response.get("broker_status"),
            1 if submitted_to_broker else 0,
            safe_json(broker_response),
        )
    )

    broker_order_row_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return broker_order_row_id


def insert_audit_event(event_type, message, ticker=None, severity="INFO", details=None):
    """
    Insert audit event into the database.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    event = {
        "event_type": event_type,
        "message": message,
        "ticker": ticker,
        "severity": severity,
        "details": details or {},
    }

    cursor.execute(
        """
        INSERT INTO audit_events (
            created_at,
            event_type,
            ticker,
            message,
            severity,
            raw_event_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event_type,
            ticker,
            message,
            severity,
            safe_json(event),
        )
    )

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return event_id


def insert_system_event(event_type, component, status, message, details=None):
    """
    Insert system event into the database.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    event = {
        "event_type": event_type,
        "component": component,
        "status": status,
        "message": message,
        "details": details or {},
    }

    cursor.execute(
        """
        INSERT INTO system_events (
            created_at,
            event_type,
            component,
            status,
            message,
            raw_event_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event_type,
            component,
            status,
            message,
            safe_json(event),
        )
    )

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return event_id


def read_table(table_name, limit=100):
    """
    Read recent rows from a database table.
    """

    allowed_tables = [
        "signals",
        "order_proposals",
        "risk_checks",
        "broker_orders",
        "audit_events",
        "system_events",
        "order_state_events",
        "order_current_state",
        "order_fills",
        "slippage_summary",
    ]

    if table_name not in allowed_tables:
        raise ValueError(f"Unsupported table: {table_name}")

    initialize_trading_database()

    conn = get_database_connection()

    query = f"""
        SELECT *
        FROM {table_name}
        ORDER BY id DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=(int(limit),))
    conn.close()

    return df


def get_database_status():
    """
    Return database file and table status.
    """

    initialize_trading_database()

    table_names = [
        "signals",
        "order_proposals",
        "risk_checks",
        "broker_orders",
        "audit_events",
        "system_events",
    ]

    conn = get_database_connection()
    cursor = conn.cursor()

    table_status = []

    for table in table_names:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cursor.fetchone()[0]

        table_status.append({
            "table": table,
            "rows": row_count
        })

    conn.close()

    return {
        "database_file": str(DATABASE_FILE),
        "database_exists": DATABASE_FILE.exists(),
        "tables": table_status,
    }
