
"""
30-Day Paper Trading Test Tracker

This module tracks the IBKR paper trading validation phase.

It records:
- daily test notes
- signals reviewed
- proposals created
- paper orders submitted
- risk blocks
- errors
- readiness review notes

This does not connect to IBKR.
This does not place orders.
"""

from pathlib import Path
from datetime import datetime
import pandas as pd


PROJECT_PATH = Path(__file__).resolve().parent
PAPER_TEST_PATH = PROJECT_PATH / "paper_test"
PAPER_TEST_LOG_FILE = PAPER_TEST_PATH / "paper_trading_30_day_log.csv"


def ensure_paper_test_folder():
    PAPER_TEST_PATH.mkdir(parents=True, exist_ok=True)


def create_paper_test_event(
    test_day=None,
    event_type="NOTE",
    ticker=None,
    strategy_name=None,
    signal=None,
    proposal_status=None,
    risk_status=None,
    manual_decision=None,
    broker_order_status=None,
    order_id=None,
    position_status=None,
    pnl_note=None,
    error_note=None,
    review_note=None,
    readiness_status="not_reviewed",
    details=None
):
    """
    Create one paper test tracking event.
    """

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_day": test_day,
        "event_type": event_type,
        "ticker": ticker,
        "strategy_name": strategy_name,
        "signal": signal,
        "proposal_status": proposal_status,
        "risk_status": risk_status,
        "manual_decision": manual_decision,
        "broker_order_status": broker_order_status,
        "order_id": order_id,
        "position_status": position_status,
        "pnl_note": pnl_note,
        "error_note": error_note,
        "review_note": review_note,
        "readiness_status": readiness_status,
        "details": str(details or {})
    }


def append_paper_test_event(event):
    """
    Append one event to the 30-day paper test CSV.
    """

    ensure_paper_test_folder()

    event_df = pd.DataFrame([event])

    if PAPER_TEST_LOG_FILE.exists():
        existing_df = pd.read_csv(PAPER_TEST_LOG_FILE)
        updated_df = pd.concat([existing_df, event_df], ignore_index=True)
    else:
        updated_df = event_df

    updated_df.to_csv(PAPER_TEST_LOG_FILE, index=False)

    return PAPER_TEST_LOG_FILE


def log_paper_test_event(**kwargs):
    """
    Create and append paper test event in one call.
    """

    event = create_paper_test_event(**kwargs)
    log_file = append_paper_test_event(event)

    return {
        "event": event,
        "log_file": str(log_file)
    }


def read_paper_test_log(limit=100):
    """
    Read latest paper test log records.
    """

    ensure_paper_test_folder()

    if not PAPER_TEST_LOG_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(PAPER_TEST_LOG_FILE)

    if df.empty:
        return df

    return df.tail(limit)


def summarize_paper_test_log():
    """
    Produce a simple summary of the paper test log.
    """

    df = read_paper_test_log(limit=100000)

    if df.empty:
        return {
            "total_events": 0,
            "unique_test_days": 0,
            "signals_reviewed": 0,
            "orders_submitted": 0,
            "risk_blocks": 0,
            "errors": 0,
            "readiness_status_counts": {}
        }

    event_counts = df["event_type"].value_counts().to_dict() if "event_type" in df.columns else {}
    readiness_counts = df["readiness_status"].value_counts().to_dict() if "readiness_status" in df.columns else {}

    return {
        "total_events": len(df),
        "unique_test_days": df["test_day"].nunique() if "test_day" in df.columns else 0,
        "signals_reviewed": event_counts.get("SIGNAL_REVIEW", 0),
        "orders_submitted": event_counts.get("PAPER_ORDER_SUBMITTED", 0),
        "risk_blocks": event_counts.get("RISK_BLOCK", 0),
        "errors": event_counts.get("ERROR", 0),
        "readiness_status_counts": readiness_counts
    }


def clear_paper_test_log():
    """
    Clear paper trading test log.

    Use carefully for development/testing only.
    """

    ensure_paper_test_folder()

    if PAPER_TEST_LOG_FILE.exists():
        PAPER_TEST_LOG_FILE.unlink()

    return True
