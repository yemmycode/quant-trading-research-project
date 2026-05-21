
"""
Live Trading Readiness Checklist

This module evaluates whether the system is ready to even consider
very small live manual testing.

It does not enable live trading.
It does not connect to IBKR.
It does not place orders.
"""

from pathlib import Path
from datetime import datetime
import json
import pandas as pd


PROJECT_PATH = Path(__file__).resolve().parent
READINESS_PATH = PROJECT_PATH / "readiness"
READINESS_FILE = READINESS_PATH / "live_trading_readiness.json"


DEFAULT_CHECKLIST = {
    "ibkr_account_available": False,
    "tws_or_gateway_installed": False,
    "ibkr_paper_login_confirmed": False,
    "ibkr_api_connection_tested": False,
    "ibkr_account_info_tested": False,
    "ibkr_positions_tested": False,
    "ibkr_market_data_tested": False,
    "ibkr_paper_order_submitted": False,
    "ibkr_paper_order_cancelled": False,
    "risk_manager_tested": False,
    "emergency_stop_tested": False,
    "manual_confirmation_tested": False,
    "trade_audit_log_active": False,
    "paper_test_tracker_active": False,
    "daily_report_available": False,
    "weekly_review_available": False,
    "thirty_day_paper_test_completed": False,
    "no_unresolved_errors": False,
    "live_mode_lock_reviewed": False,
    "small_capital_plan_defined": False,
    "live_trading_disabled_in_config": True,
}


REQUIRED_FOR_SMALL_LIVE_TEST = list(DEFAULT_CHECKLIST.keys())


def ensure_readiness_folder():
    READINESS_PATH.mkdir(parents=True, exist_ok=True)


def default_readiness_state():
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_by": "system",
        "checklist": DEFAULT_CHECKLIST.copy(),
        "notes": "",
    }


def write_readiness_state(state):
    ensure_readiness_folder()

    with open(READINESS_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

    return state


def read_readiness_state():
    """
    Read readiness state safely.

    If the JSON file is missing, corrupted, or incomplete,
    this function repairs it automatically.
    """

    ensure_readiness_folder()

    if not READINESS_FILE.exists():
        state = default_readiness_state()
        write_readiness_state(state)
        return state

    try:
        with open(READINESS_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = default_readiness_state()
        state["notes"] = "Readiness file was corrupted and has been reset."
        write_readiness_state(state)
        return state

    if not isinstance(state, dict):
        state = default_readiness_state()
        state["notes"] = "Readiness state was invalid and has been reset."
        write_readiness_state(state)
        return state

    if "checklist" not in state or not isinstance(state.get("checklist"), dict):
        state["checklist"] = DEFAULT_CHECKLIST.copy()

    for key, default_value in DEFAULT_CHECKLIST.items():
        if key not in state["checklist"]:
            state["checklist"][key] = default_value

    if "updated_at" not in state:
        state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "updated_by" not in state:
        state["updated_by"] = "system"

    if "notes" not in state:
        state["notes"] = ""

    write_readiness_state(state)

    return state


def update_readiness_item(item_key, value, updated_by="user", notes=None):
    state = read_readiness_state()

    if item_key not in DEFAULT_CHECKLIST:
        raise ValueError(f"Unknown readiness checklist item: {item_key}")

    state["checklist"][item_key] = bool(value)
    state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["updated_by"] = updated_by

    if notes is not None:
        state["notes"] = notes

    return write_readiness_state(state)


def bulk_update_readiness(checklist_updates, updated_by="user", notes=None):
    state = read_readiness_state()

    for item_key, value in checklist_updates.items():
        if item_key not in DEFAULT_CHECKLIST:
            raise ValueError(f"Unknown readiness checklist item: {item_key}")

        state["checklist"][item_key] = bool(value)

    state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["updated_by"] = updated_by

    if notes is not None:
        state["notes"] = notes

    return write_readiness_state(state)


def evaluate_live_readiness():
    state = read_readiness_state()
    checklist = state.get("checklist", {})

    missing_items = [
        item for item in REQUIRED_FOR_SMALL_LIVE_TEST
        if not checklist.get(item, False)
    ]

    completed_items = [
        item for item in REQUIRED_FOR_SMALL_LIVE_TEST
        if checklist.get(item, False)
    ]

    total_required = len(REQUIRED_FOR_SMALL_LIVE_TEST)
    completed_count = len(completed_items)
    missing_count = len(missing_items)

    readiness_score = completed_count / total_required if total_required else 0
    ready_for_small_live_test = missing_count == 0

    if ready_for_small_live_test:
        status = "checklist_complete"
        recommendation = (
            "Checklist is complete. Very small live manual testing may be considered only after final review. "
            "Do not enable automated live trading."
        )
    elif readiness_score >= 0.75:
        status = "almost_ready_but_blocked"
        recommendation = (
            "Most readiness items are complete, but live testing should not start until all required items are complete."
        )
    elif readiness_score >= 0.50:
        status = "partially_ready"
        recommendation = (
            "System is partially ready, but more paper testing and safety validation are required."
        )
    else:
        status = "not_ready"
        recommendation = (
            "System is not ready for live trading. Continue paper testing and validation."
        )

    return {
        "ready_for_small_live_test": ready_for_small_live_test,
        "status": status,
        "readiness_score": round(readiness_score, 4),
        "completed_count": completed_count,
        "missing_count": missing_count,
        "total_required": total_required,
        "completed_items": completed_items,
        "missing_items": missing_items,
        "recommendation": recommendation,
        "updated_at": state.get("updated_at"),
        "updated_by": state.get("updated_by"),
        "notes": state.get("notes", ""),
    }


def readiness_to_dataframe():
    state = read_readiness_state()
    checklist = state.get("checklist", {})

    rows = []

    for key, value in checklist.items():
        rows.append({
            "checklist_item": key,
            "completed": bool(value),
            "required_for_small_live_test": key in REQUIRED_FOR_SMALL_LIVE_TEST
        })

    return pd.DataFrame(rows)


def reset_readiness_state():
    state = default_readiness_state()
    return write_readiness_state(state)
