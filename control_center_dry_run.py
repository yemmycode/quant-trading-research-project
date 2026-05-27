
"""
Trading Control Center Dry Run

This module records an end-to-end dry run from the Trading Control Center.

It does not connect to IBKR.
It does not submit broker orders.
It does not enable live trading.
"""

from datetime import datetime

from trading_control_center import run_trading_control_center_check
from trading_database import (
    initialize_trading_database,
    get_database_connection,
    safe_json,
)


def initialize_control_center_dry_run_table():
    """
    Create dry run table.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trading_control_center_dry_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            ticker TEXT,
            strategy_name TEXT,
            quantity REAL,
            order_type TEXT,
            limit_price REAL,
            dry_run_status TEXT,
            final_decision TEXT,
            blocker_count INTEGER,
            warning_count INTEGER,
            would_submit_to_broker INTEGER,
            submitted_to_broker INTEGER,
            raw_dry_run_json TEXT
        )
    """)

    conn.commit()
    conn.close()

    return True


def classify_dry_run_status(control_result):
    """
    Classify the dry run based on the Trading Control Center result.
    """

    if not isinstance(control_result, dict):
        return "invalid_result"

    final_decision = control_result.get("final_decision")

    if final_decision == "ready_for_manual_paper_review":
        return "dry_run_ready_for_manual_review"

    if final_decision == "blocked":
        return "dry_run_blocked"

    return "dry_run_unknown"


def record_control_center_dry_run(
    control_result,
    ticker=None,
    strategy_name=None,
    quantity=None,
    order_type=None,
    limit_price=None,
):
    """
    Save dry run result to SQLite.
    """

    initialize_control_center_dry_run_table()

    dry_run_status = classify_dry_run_status(control_result)

    would_submit_to_broker = dry_run_status == "dry_run_ready_for_manual_review"

    payload = {
        "ticker": ticker or control_result.get("ticker"),
        "strategy_name": strategy_name or control_result.get("strategy_name"),
        "quantity": quantity,
        "order_type": order_type,
        "limit_price": limit_price,
        "dry_run_status": dry_run_status,
        "would_submit_to_broker": would_submit_to_broker,
        "submitted_to_broker": False,
        "control_result": control_result,
    }

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO trading_control_center_dry_runs (
            created_at,
            ticker,
            strategy_name,
            quantity,
            order_type,
            limit_price,
            dry_run_status,
            final_decision,
            blocker_count,
            warning_count,
            would_submit_to_broker,
            submitted_to_broker,
            raw_dry_run_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            payload["ticker"],
            payload["strategy_name"],
            quantity,
            order_type,
            limit_price,
            dry_run_status,
            control_result.get("final_decision"),
            len(control_result.get("blockers", []) or []),
            len(control_result.get("warnings", []) or []),
            1 if would_submit_to_broker else 0,
            0,
            safe_json(payload),
        )
    )

    dry_run_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "recorded": True,
        "dry_run_id": dry_run_id,
        "dry_run_status": dry_run_status,
        "would_submit_to_broker": would_submit_to_broker,
        "submitted_to_broker": False,
        "message": (
            "Dry run completed. No broker order was submitted."
            if would_submit_to_broker
            else "Dry run completed and workflow was blocked before broker submission."
        ),
    }


def run_control_center_dry_run(
    ticker="SPY",
    strategy_name="moving_average",
    short_window=20,
    long_window=50,
    quantity=1,
    order_type="LMT",
    limit_price=None,
    paper_broker=None,
    allow_after_hours=False,
    allow_short_selling=False,
    allow_add_to_existing=False,
    manual_reference_price=None,
):
    """
    Run the Trading Control Center workflow and record it as a dry run.

    This never submits to the broker.
    """

    control_result = run_trading_control_center_check(
        ticker=ticker,
        strategy_name=strategy_name,
        short_window=short_window,
        long_window=long_window,
        quantity=quantity,
        order_type=order_type,
        limit_price=limit_price,
        paper_broker=paper_broker,
        allow_after_hours=allow_after_hours,
        allow_short_selling=allow_short_selling,
        allow_add_to_existing=allow_add_to_existing,
        manual_reference_price=manual_reference_price,
    )

    dry_run_record = record_control_center_dry_run(
        control_result=control_result,
        ticker=ticker,
        strategy_name=strategy_name,
        quantity=quantity,
        order_type=order_type,
        limit_price=limit_price,
    )

    return {
        "dry_run_record": dry_run_record,
        "control_result": control_result,
    }


def read_control_center_dry_runs(limit=100):
    """
    Read recent dry runs.
    """

    initialize_control_center_dry_run_table()

    import pandas as pd

    conn = get_database_connection()

    query = """
        SELECT *
        FROM trading_control_center_dry_runs
        ORDER BY id DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=(int(limit),))
    conn.close()

    return df


def summarize_control_center_dry_runs(limit=500):
    """
    Summarize dry runs.
    """

    df = read_control_center_dry_runs(limit=limit)

    if df.empty:
        return {
            "has_data": False,
            "total_dry_runs": 0,
            "ready_dry_runs": 0,
            "blocked_dry_runs": 0,
            "message": "No dry runs found.",
        }

    total = len(df)
    ready = int(df["would_submit_to_broker"].sum())
    blocked = total - ready

    return {
        "has_data": True,
        "total_dry_runs": int(total),
        "ready_dry_runs": int(ready),
        "blocked_dry_runs": int(blocked),
        "ready_rate": round(ready / total, 4) if total else 0.0,
        "latest_status": df.iloc[0]["dry_run_status"],
        "latest_ticker": df.iloc[0]["ticker"],
        "latest_created_at": df.iloc[0]["created_at"],
    }
