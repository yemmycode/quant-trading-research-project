
"""
Persistent Safety Manager

This module controls emergency stop state.

The emergency stop is saved to a JSON file so it remains active
across app restarts and Python sessions.
"""

from pathlib import Path
from datetime import datetime
import json


PROJECT_PATH = Path(__file__).resolve().parent
SAFETY_PATH = PROJECT_PATH / "safety"
EMERGENCY_STOP_FILE = SAFETY_PATH / "emergency_stop.json"


def ensure_safety_folder():
    """
    Ensure safety folder exists.
    """

    SAFETY_PATH.mkdir(parents=True, exist_ok=True)


def default_emergency_stop_state():
    """
    Default emergency stop state.
    """

    return {
        "active": False,
        "reason": "",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_by": "system"
    }


def read_emergency_stop_state():
    """
    Read emergency stop state from JSON file.

    If file does not exist, create default inactive state.
    """

    ensure_safety_folder()

    if not EMERGENCY_STOP_FILE.exists():
        state = default_emergency_stop_state()
        write_emergency_stop_state(state)
        return state

    try:
        with open(EMERGENCY_STOP_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        required_keys = ["active", "reason", "updated_at", "updated_by"]

        for key in required_keys:
            if key not in state:
                state[key] = default_emergency_stop_state()[key]

        return state

    except Exception:
        state = {
            "active": True,
            "reason": "Emergency stop activated because safety file could not be read.",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_by": "system"
        }

        write_emergency_stop_state(state)
        return state


def write_emergency_stop_state(state):
    """
    Write emergency stop state to JSON file.
    """

    ensure_safety_folder()

    with open(EMERGENCY_STOP_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

    return state


def activate_emergency_stop(reason="Manual emergency stop activated.", updated_by="user"):
    """
    Activate emergency stop.
    """

    state = {
        "active": True,
        "reason": reason,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_by": updated_by
    }

    return write_emergency_stop_state(state)


def deactivate_emergency_stop(reason="Emergency stop deactivated.", updated_by="user"):
    """
    Deactivate emergency stop.
    """

    state = {
        "active": False,
        "reason": reason,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_by": updated_by
    }

    return write_emergency_stop_state(state)


def is_emergency_stop_active():
    """
    Return True if emergency stop is active.
    """

    state = read_emergency_stop_state()
    return bool(state.get("active", False))


def get_emergency_stop_reason():
    """
    Return emergency stop reason.
    """

    state = read_emergency_stop_state()
    return state.get("reason", "")


def require_emergency_stop_inactive():
    """
    Raise PermissionError if emergency stop is active.
    """

    state = read_emergency_stop_state()

    if state.get("active", False):
        raise PermissionError(
            f"Emergency stop is active. Reason: {state.get('reason', '')}"
        )

    return True
