
"""
Live Mode Lock

This module protects the system from accidentally enabling live trading.

It does not enable live trading.
It does not connect to IBKR.
It does not place orders.

It only checks whether every required live-mode condition is satisfied.
"""

from datetime import datetime

from safety_manager import read_emergency_stop_state
from live_readiness import evaluate_live_readiness
from live_warning import is_live_warning_acknowledged


def get_live_mode_config_snapshot():
    """
    Read current live/broker configuration from config.py.
    """

    from config import (
        EXECUTION_MODE,
        DEFAULT_BROKER,
        ALLOW_LIVE_TRADING,
        LIVE_TRADING_ENABLED,
        REQUIRE_MANUAL_CONFIRMATION,
        IBKR_TRADING_MODE,
        IBKR_READ_ONLY,
        IBKR_ENABLE_ORDERS
    )

    return {
        "EXECUTION_MODE": EXECUTION_MODE,
        "DEFAULT_BROKER": DEFAULT_BROKER,
        "ALLOW_LIVE_TRADING": ALLOW_LIVE_TRADING,
        "LIVE_TRADING_ENABLED": LIVE_TRADING_ENABLED,
        "REQUIRE_MANUAL_CONFIRMATION": REQUIRE_MANUAL_CONFIRMATION,
        "IBKR_TRADING_MODE": IBKR_TRADING_MODE,
        "IBKR_READ_ONLY": IBKR_READ_ONLY,
        "IBKR_ENABLE_ORDERS": IBKR_ENABLE_ORDERS,
    }


def evaluate_live_mode_lock():
    """
    Evaluate whether live manual trading mode is unlocked.

    Expected result for now:
    - locked = True
    - live_mode_allowed = False
    """

    config_snapshot = get_live_mode_config_snapshot()
    emergency_state = read_emergency_stop_state()
    readiness_eval = evaluate_live_readiness()

    checks = {
        "execution_mode_is_live_manual": config_snapshot["EXECUTION_MODE"] == "LIVE_MANUAL",
        "default_broker_is_ibkr": config_snapshot["DEFAULT_BROKER"] == "ibkr",
        "allow_live_trading_true": config_snapshot["ALLOW_LIVE_TRADING"] is True,
        "live_trading_enabled_true": config_snapshot["LIVE_TRADING_ENABLED"] is True,
        "manual_confirmation_required": config_snapshot["REQUIRE_MANUAL_CONFIRMATION"] is True,
        "ibkr_trading_mode_live": config_snapshot["IBKR_TRADING_MODE"] == "live",
        "ibkr_read_only_false": config_snapshot["IBKR_READ_ONLY"] is False,
        "ibkr_enable_orders_true": config_snapshot["IBKR_ENABLE_ORDERS"] is True,
        "emergency_stop_inactive": emergency_state.get("active", False) is False,
        "readiness_checklist_complete": readiness_eval.get("ready_for_small_live_test", False) is True,
    }

    failed_checks = [
        check_name for check_name, passed in checks.items()
        if not passed
    ]

    passed_checks = [
        check_name for check_name, passed in checks.items()
        if passed
    ]

    live_mode_allowed = len(failed_checks) == 0

    if live_mode_allowed:
        status = "unlocked"
        message = (
            "Live manual mode lock is unlocked. "
            "This still does not mean auto-trading is allowed. "
            "Only very small manual live testing may be considered after final warning and dry-run review."
        )
    else:
        status = "locked"
        message = (
            "Live mode is locked. One or more required safety conditions are not satisfied."
        )

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "live_mode_allowed": live_mode_allowed,
        "locked": not live_mode_allowed,
        "status": status,
        "message": message,
        "checks": checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "config_snapshot": config_snapshot,
        "emergency_stop": emergency_state,
        "readiness": readiness_eval,
    }


def require_live_mode_unlocked():
    """
    Raise PermissionError unless the live mode lock is fully unlocked.
    """

    lock_eval = evaluate_live_mode_lock()

    if not lock_eval["live_mode_allowed"]:
        raise PermissionError(
            "Live mode is locked. Failed checks: "
            + ", ".join(lock_eval["failed_checks"])
        )

    return True


def explain_live_mode_lock():
    """
    Return a simplified explanation for dashboard display.
    """

    lock_eval = evaluate_live_mode_lock()

    return {
        "status": lock_eval["status"],
        "live_mode_allowed": lock_eval["live_mode_allowed"],
        "message": lock_eval["message"],
        "failed_checks": lock_eval["failed_checks"],
        "passed_checks": lock_eval["passed_checks"],
    }
