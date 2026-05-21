
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


def generate_daily_paper_report(test_day=None):
    """
    Generate a daily report from the 30-day paper trading log.

    If test_day is provided, report only that test day.
    If test_day is None, report the latest available test day.
    """

    df = read_paper_test_log(limit=100000)

    if df.empty:
        return {
            "has_data": False,
            "message": "No paper trading test records found.",
            "report": {}
        }

    if test_day is None:
        test_day = int(df["test_day"].dropna().max()) if df["test_day"].notna().any() else None

    if test_day is not None:
        day_df = df[df["test_day"] == test_day].copy()
    else:
        day_df = df.copy()

    if day_df.empty:
        return {
            "has_data": False,
            "message": f"No paper trading records found for test_day={test_day}.",
            "report": {}
        }

    event_counts = day_df["event_type"].value_counts().to_dict() if "event_type" in day_df.columns else {}
    signal_counts = day_df["signal"].value_counts().to_dict() if "signal" in day_df.columns else {}
    risk_counts = day_df["risk_status"].value_counts().to_dict() if "risk_status" in day_df.columns else {}
    manual_counts = day_df["manual_decision"].value_counts().to_dict() if "manual_decision" in day_df.columns else {}
    broker_status_counts = day_df["broker_order_status"].value_counts().to_dict() if "broker_order_status" in day_df.columns else {}
    readiness_counts = day_df["readiness_status"].value_counts().to_dict() if "readiness_status" in day_df.columns else {}

    latest_notes = []

    note_columns = [
        "review_note",
        "pnl_note",
        "error_note",
        "position_status"
    ]

    for _, row in day_df.iterrows():
        note_item = {
            "timestamp": row.get("timestamp", ""),
            "event_type": row.get("event_type", ""),
            "ticker": row.get("ticker", ""),
            "strategy_name": row.get("strategy_name", "")
        }

        has_note = False

        for col in note_columns:
            value = row.get(col, "")
            if isinstance(value, str) and value.strip():
                note_item[col] = value
                has_note = True

        if has_note:
            latest_notes.append(note_item)

    report = {
        "test_day": test_day,
        "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_events": len(day_df),
        "event_counts": event_counts,
        "signal_counts": signal_counts,
        "risk_status_counts": risk_counts,
        "manual_decision_counts": manual_counts,
        "broker_order_status_counts": broker_status_counts,
        "readiness_status_counts": readiness_counts,
        "signals_reviewed": event_counts.get("SIGNAL_REVIEW", 0),
        "paper_orders_submitted": event_counts.get("PAPER_ORDER_SUBMITTED", 0),
        "risk_blocks": event_counts.get("RISK_BLOCK", 0),
        "errors": event_counts.get("ERROR", 0),
        "latest_notes": latest_notes[-10:],
    }

    return {
        "has_data": True,
        "message": "Daily paper trading report generated.",
        "report": report
    }


def save_daily_paper_report(test_day=None):
    """
    Save a daily paper trading report as CSV-friendly summary.
    """

    ensure_paper_test_folder()

    report_result = generate_daily_paper_report(test_day=test_day)

    report_file = PAPER_TEST_PATH / "daily_paper_trading_report.csv"

    report = report_result.get("report", {})

    if not report:
        summary_row = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_day": test_day,
            "has_data": False,
            "message": report_result.get("message")
        }
    else:
        summary_row = {
            "generated_at": report.get("date_generated"),
            "test_day": report.get("test_day"),
            "has_data": True,
            "total_events": report.get("total_events"),
            "signals_reviewed": report.get("signals_reviewed"),
            "paper_orders_submitted": report.get("paper_orders_submitted"),
            "risk_blocks": report.get("risk_blocks"),
            "errors": report.get("errors"),
            "event_counts": str(report.get("event_counts")),
            "signal_counts": str(report.get("signal_counts")),
            "risk_status_counts": str(report.get("risk_status_counts")),
            "manual_decision_counts": str(report.get("manual_decision_counts")),
            "broker_order_status_counts": str(report.get("broker_order_status_counts")),
            "readiness_status_counts": str(report.get("readiness_status_counts")),
            "latest_notes": str(report.get("latest_notes"))
        }

    summary_df = pd.DataFrame([summary_row])

    if report_file.exists():
        existing_df = pd.read_csv(report_file)
        updated_df = pd.concat([existing_df, summary_df], ignore_index=True)
    else:
        updated_df = summary_df

    updated_df.to_csv(report_file, index=False)

    return {
        "report_file": str(report_file),
        "report_result": report_result
    }
