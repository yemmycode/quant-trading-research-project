
"""
Environment Reset Checklist

This module tracks whether the user has manually returned the trading system
to a safer environment after broker testing.

It does not change .env.
It does not connect to IBKR.
It does not place orders.
"""

from pathlib import Path
from datetime import datetime
import json
import pandas as pd


PROJECT_PATH = Path(__file__).resolve().parent
RESET_PATH = PROJECT_PATH / "readiness"
RESET_FILE = RESET_PATH / "environment_reset_checklist.json"


RESET_CHECKLIST = {
    "ibkr_read_only_true_in_env": False,
    "ibkr_enable_orders_false_in_env": False,
    "allow_live_trading_false": False,
    "live_trading_enabled_false": False,
    "tws_read_only_api_checked": False,
    "paper_orders_reviewed_or_cancelled": False,
    "emergency_stop_reviewed": False,
    "audit_log_reviewed": False,
    "broker_environment_panel_checked": False,
    "streamlit_restarted_after_env_change": False,
}


def ensure_reset_folder():
    RESET_PATH.mkdir(parents=True, exist_ok=True)


def default_reset_state():
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_by": "system",
        "checklist": RESET_CHECKLIST.copy(),
        "notes": "",
    }


def write_reset_state(state):
    ensure_reset_folder()

    with open(RESET_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

    return state


def read_reset_state():
    ensure_reset_folder()

    if not RESET_FILE.exists():
        state = default_reset_state()
        write_reset_state(state)
        return state

    try:
        with open(RESET_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = default_reset_state()
        state["notes"] = "Reset checklist file was corrupted and has been reset."
        write_reset_state(state)
        return state

    if not isinstance(state, dict):
        state = default_reset_state()

    if "checklist" not in state or not isinstance(state.get("checklist"), dict):
        state["checklist"] = RESET_CHECKLIST.copy()

    for key, default_value in RESET_CHECKLIST.items():
        if key not in state["checklist"]:
            state["checklist"][key] = default_value

    if "updated_at" not in state:
        state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "updated_by" not in state:
        state["updated_by"] = "system"

    if "notes" not in state:
        state["notes"] = ""

    write_reset_state(state)

    return state


def bulk_update_reset_checklist(checklist_updates, updated_by="user", notes=None):
    state = read_reset_state()

    for item_key, value in checklist_updates.items():
        if item_key not in RESET_CHECKLIST:
            raise ValueError(f"Unknown reset checklist item: {item_key}")

        state["checklist"][item_key] = bool(value)

    state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["updated_by"] = updated_by

    if notes is not None:
        state["notes"] = notes

    return write_reset_state(state)


def evaluate_environment_reset():
    state = read_reset_state()
    checklist = state.get("checklist", {})

    missing_items = [
        item for item in RESET_CHECKLIST
        if not checklist.get(item, False)
    ]

    completed_items = [
        item for item in RESET_CHECKLIST
        if checklist.get(item, False)
    ]

    total_items = len(RESET_CHECKLIST)
    completed_count = len(completed_items)
    missing_count = len(missing_items)

    reset_score = completed_count / total_items if total_items else 0
    reset_complete = missing_count == 0

    if reset_complete:
        status = "reset_complete"
        recommendation = "Environment reset checklist is complete. System appears returned to safer mode."
    elif reset_score >= 0.70:
        status = "almost_reset"
        recommendation = "Most reset items are complete, but finish all items before continuing normal use."
    else:
        status = "reset_incomplete"
        recommendation = "Environment reset is incomplete. Review broker/order settings before continuing."

    return {
        "status": status,
        "reset_complete": reset_complete,
        "reset_score": round(reset_score, 4),
        "completed_count": completed_count,
        "missing_count": missing_count,
        "total_items": total_items,
        "completed_items": completed_items,
        "missing_items": missing_items,
        "recommendation": recommendation,
        "updated_at": state.get("updated_at"),
        "updated_by": state.get("updated_by"),
        "notes": state.get("notes", ""),
    }


def reset_checklist_to_default():
    state = default_reset_state()
    return write_reset_state(state)


def reset_checklist_to_dataframe():
    state = read_reset_state()
    checklist = state.get("checklist", {})

    rows = []

    for key, value in checklist.items():
        rows.append({
            "reset_item": key,
            "completed": bool(value)
        })

    return pd.DataFrame(rows)
