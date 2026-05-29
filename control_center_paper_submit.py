
"""
Trading Control Center Paper Submission

Controlled paper-only submission from the Trading Control Center.

This module does not enable live trading.
It submits only when the control-center decision is ready and manual confirmation is provided.
"""

from datetime import datetime

from broker_factory import get_broker
from order_state_manager import create_order_state_from_proposal, record_broker_submission_state
from trade_audit import log_audit_event
from trading_database import insert_broker_order, safe_json, initialize_trading_database, get_database_connection


def initialize_control_center_paper_submit_table():
    """
    Create table for Trading Control Center paper submissions.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trading_control_center_paper_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            order_type TEXT,
            limit_price REAL,
            submitted_to_broker INTEGER,
            broker_status TEXT,
            broker_order_id TEXT,
            control_center_decision TEXT,
            manual_confirmation TEXT,
            raw_submission_json TEXT
        )
    """)

    conn.commit()
    conn.close()

    return True


def save_control_center_paper_submission(submission_result):
    """
    Save controlled paper submission result.
    """

    initialize_control_center_paper_submit_table()

    conn = get_database_connection()
    cursor = conn.cursor()

    broker_result = submission_result.get("broker_result", {}) or {}
    proposal = submission_result.get("proposal", {}) or {}

    cursor.execute(
        """
        INSERT INTO trading_control_center_paper_submissions (
            created_at,
            ticker,
            side,
            quantity,
            order_type,
            limit_price,
            submitted_to_broker,
            broker_status,
            broker_order_id,
            control_center_decision,
            manual_confirmation,
            raw_submission_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            proposal.get("ticker"),
            proposal.get("side"),
            proposal.get("quantity"),
            proposal.get("order_type"),
            proposal.get("limit_price"),
            1 if submission_result.get("submitted_to_broker") else 0,
            broker_result.get("order_status") or broker_result.get("broker_status"),
            broker_result.get("order_id") or broker_result.get("broker_order_id"),
            submission_result.get("control_center_decision"),
            submission_result.get("manual_confirmation"),
            safe_json(submission_result),
        )
    )

    submission_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return submission_id


def submit_control_center_paper_order(
    control_result,
    manual_confirmation,
):
    """
    Submit paper order only if all Trading Control Center checks passed.

    Required manual confirmation:
    SUBMIT PAPER
    """

    initialize_control_center_paper_submit_table()

    if not isinstance(control_result, dict):
        raise ValueError("control_result must be a dictionary.")

    confirmation_text = str(manual_confirmation or "").strip().upper()

    if confirmation_text != "SUBMIT PAPER":
        raise PermissionError("Manual confirmation must be exactly: SUBMIT PAPER")

    if control_result.get("final_decision") != "ready_for_manual_paper_review":
        raise PermissionError(
            f"Control Center decision is not ready: {control_result.get('final_decision')}"
        )

    if control_result.get("submitted_to_broker"):
        raise PermissionError("This control result is already marked as submitted.")

    workflow_steps = control_result.get("workflow_steps", {}) or {}
    proposal = workflow_steps.get("order_proposal", {}) or {}

    if not proposal:
        raise ValueError("No order proposal found in control result.")

    if not proposal.get("actionable", False):
        raise PermissionError("Order proposal is not actionable.")

    ticker = proposal.get("ticker")
    side = proposal.get("side")
    quantity = proposal.get("quantity")
    order_type = proposal.get("order_type")
    limit_price = proposal.get("limit_price")

    if not ticker or not side or not quantity or not order_type:
        raise ValueError("Proposal is missing required order fields.")

    broker = None

    try:
        broker = get_broker("ibkr")

        if str(order_type).upper() == "LMT":
            broker_result = broker.submit_order(
                ticker=ticker,
                side=side,
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price
            )
        else:
            broker_result = broker.submit_order(
                ticker=ticker,
                side=side,
                quantity=quantity,
                order_type=order_type,
                limit_price=None
            )

        submission_result = {
            "submitted_to_broker": True,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "control_center_decision": control_result.get("final_decision"),
            "manual_confirmation": manual_confirmation,
            "proposal": proposal,
            "broker_result": broker_result,
        }

        try:
            broker_order_row_id = insert_broker_order(
                broker_response={
                    **broker_result,
                    "ticker": ticker,
                    "side": side,
                    "quantity": quantity,
                    "order_type": order_type,
                    "limit_price": limit_price,
                    "execution_mode": "BROKER_PAPER",
                    "broker_name": "ibkr",
                },
                proposal_id=None,
                risk_check_id=None,
                submitted_to_broker=True
            )

            submission_result["broker_order_row_id"] = broker_order_row_id

        except Exception as db_error:
            submission_result["broker_order_db_error"] = f"{type(db_error).__name__}: {db_error}"

        try:
            state_proposal = {
                "ticker": ticker,
                "side": side,
                "quantity": quantity,
                "order_type": order_type,
                "limit_price": limit_price,
                "estimated_order_value": proposal.get("estimated_order_value"),
                "proposal_status": "control_center_paper_submitted",
                "actionable": True,
                "reason": "Paper order submitted from Trading Control Center."
            }

            state_create_result = create_order_state_from_proposal(
                proposal=state_proposal,
                proposal_id=None
            )

            state_submit_result = record_broker_submission_state(
                order_key=state_create_result["order_key"],
                broker_response={
                    **broker_result,
                    "ticker": ticker,
                    "side": side,
                    "quantity": quantity,
                    "order_type": order_type,
                    "limit_price": limit_price,
                    "execution_mode": "BROKER_PAPER",
                    "broker_name": "ibkr",
                },
                broker_order_row_id=submission_result.get("broker_order_row_id")
            )

            submission_result["order_state_created"] = state_create_result
            submission_result["order_state_submitted"] = state_submit_result

        except Exception as state_error:
            submission_result["order_state_error"] = f"{type(state_error).__name__}: {state_error}"

        try:
            log_audit_event(
                event_type="TCC_IBKR_PAPER_ORDER_SUBMITTED",
                ticker=ticker,
                side=side,
                quantity=quantity,
                order_type=order_type,
                limit_price=limit_price,
                broker_name="ibkr",
                execution_mode="BROKER_PAPER",
                broker_status="submitted",
                message="Trading Control Center submitted controlled IBKR paper order.",
                details=submission_result
            )
        except Exception as audit_error:
            submission_result["audit_error"] = f"{type(audit_error).__name__}: {audit_error}"

        try:
            submission_id = save_control_center_paper_submission(submission_result)
            submission_result["paper_submission_id"] = submission_id
        except Exception as save_error:
            submission_result["paper_submission_save_error"] = f"{type(save_error).__name__}: {save_error}"

        return submission_result

    finally:
        if broker is not None:
            try:
                broker.disconnect()
            except Exception:
                pass


def read_control_center_paper_submissions(limit=100):
    """
    Read recent Trading Control Center paper submissions.
    """

    initialize_control_center_paper_submit_table()

    import pandas as pd

    conn = get_database_connection()

    query = """
        SELECT *
        FROM trading_control_center_paper_submissions
        ORDER BY id DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=(int(limit),))
    conn.close()

    return df


def summarize_control_center_paper_submissions(limit=500):
    """
    Summarize controlled paper submissions.
    """

    df = read_control_center_paper_submissions(limit=limit)

    if df.empty:
        return {
            "has_data": False,
            "total_submissions": 0,
            "submitted_count": 0,
            "message": "No Trading Control Center paper submissions found.",
        }

    total = len(df)
    submitted = int(df["submitted_to_broker"].sum())

    return {
        "has_data": True,
        "total_submissions": int(total),
        "submitted_count": int(submitted),
        "latest_ticker": df.iloc[0]["ticker"],
        "latest_side": df.iloc[0]["side"],
        "latest_status": df.iloc[0]["broker_status"],
        "latest_created_at": df.iloc[0]["created_at"],
    }
