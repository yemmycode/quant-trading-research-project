
"""
Live Trading Warning Screen

This module manages acknowledgement of live trading warnings.

It does not enable live trading.
It does not connect to IBKR.
It does not place orders.
"""

from pathlib import Path
from datetime import datetime
import json


PROJECT_PATH = Path(__file__).resolve().parent
WARNING_PATH = PROJECT_PATH / "readiness"
WARNING_FILE = WARNING_PATH / "live_trading_warning_acknowledgement.json"


WARNING_STATEMENTS = [
    "I understand that live trading involves real financial risk.",
    "I understand that I can lose money when placing live trades.",
    "I understand that backtested and paper-traded results do not guarantee future live performance.",
    "I understand that live trading must remain manual-confirmation only at this stage.",
    "I understand that this system must not be used for other people's money or public investment advice without proper legal and regulatory review.",
    "I understand that automated live trading is not enabled and should not be enabled casually.",
]


def ensure_warning_folder():
    WARNING_PATH.mkdir(parents=True, exist_ok=True)


def default_warning_state():
    return {
        "acknowledged": False,
        "acknowledged_at": "",
        "acknowledged_by": "",
        "statements": WARNING_STATEMENTS,
        "notes": "",
    }


def write_warning_state(state):
    ensure_warning_folder()

    with open(WARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

    return state


def read_warning_state():
    ensure_warning_folder()

    if not WARNING_FILE.exists():
        state = default_warning_state()
        write_warning_state(state)
        return state

    try:
        with open(WARNING_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = default_warning_state()
        state["notes"] = "Warning acknowledgement file was corrupted and has been reset."
        write_warning_state(state)
        return state

    if not isinstance(state, dict):
        state = default_warning_state()
        write_warning_state(state)
        return state

    if "acknowledged" not in state:
        state["acknowledged"] = False

    if "acknowledged_at" not in state:
        state["acknowledged_at"] = ""

    if "acknowledged_by" not in state:
        state["acknowledged_by"] = ""

    if "statements" not in state:
        state["statements"] = WARNING_STATEMENTS

    if "notes" not in state:
        state["notes"] = ""

    write_warning_state(state)

    return state


def acknowledge_live_warning(acknowledged_by="user", notes=""):
    state = {
        "acknowledged": True,
        "acknowledged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acknowledged_by": acknowledged_by,
        "statements": WARNING_STATEMENTS,
        "notes": notes,
    }

    return write_warning_state(state)


def reset_live_warning_acknowledgement():
    state = default_warning_state()
    return write_warning_state(state)


def is_live_warning_acknowledged():
    state = read_warning_state()
    return bool(state.get("acknowledged", False))


def require_live_warning_acknowledged():
    state = read_warning_state()

    if not state.get("acknowledged", False):
        raise PermissionError(
            "Live trading warning has not been acknowledged."
        )

    return True
