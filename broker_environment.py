
"""
Broker Environment Safety Classifier

This module reads current config settings and classifies the broker environment.

It does not change settings.
It does not connect to IBKR.
It does not place orders.
"""

from datetime import datetime


def get_broker_environment_snapshot():
    """
    Read current broker/execution settings from config.py.
    """

    from config import (
        EXECUTION_MODE,
        DEFAULT_BROKER,
        ALLOW_LIVE_TRADING,
        LIVE_TRADING_ENABLED,
        REQUIRE_MANUAL_CONFIRMATION,
        IBKR_TRADING_MODE,
        IBKR_PORT,
        IBKR_READ_ONLY,
        IBKR_ENABLE_ORDERS
    )

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "EXECUTION_MODE": EXECUTION_MODE,
        "DEFAULT_BROKER": DEFAULT_BROKER,
        "ALLOW_LIVE_TRADING": ALLOW_LIVE_TRADING,
        "LIVE_TRADING_ENABLED": LIVE_TRADING_ENABLED,
        "REQUIRE_MANUAL_CONFIRMATION": REQUIRE_MANUAL_CONFIRMATION,
        "IBKR_TRADING_MODE": IBKR_TRADING_MODE,
        "IBKR_PORT": IBKR_PORT,
        "IBKR_READ_ONLY": IBKR_READ_ONLY,
        "IBKR_ENABLE_ORDERS": IBKR_ENABLE_ORDERS,
    }


def classify_broker_environment():
    """
    Classify the current broker environment safety status.
    """

    snapshot = get_broker_environment_snapshot()

    execution_mode = snapshot["EXECUTION_MODE"]
    default_broker = snapshot["DEFAULT_BROKER"]
    allow_live = snapshot["ALLOW_LIVE_TRADING"]
    live_enabled = snapshot["LIVE_TRADING_ENABLED"]
    manual_required = snapshot["REQUIRE_MANUAL_CONFIRMATION"]
    ibkr_mode = snapshot["IBKR_TRADING_MODE"]
    ibkr_port = int(snapshot["IBKR_PORT"])
    ibkr_read_only = snapshot["IBKR_READ_ONLY"]
    ibkr_enable_orders = snapshot["IBKR_ENABLE_ORDERS"]

    warnings = []
    blockers = []

    if not manual_required:
        blockers.append("Manual confirmation is not required. This is unsafe.")

    # Internal simulated paper broker
    if default_broker == "paper":
        status = "SAFE_PAPER"
        message = "Using internal simulated paper broker. No real broker connection required."

        if allow_live or live_enabled:
            blockers.append("Live trading flags should not be enabled while using paper broker.")

        return {
            "status": status,
            "message": message,
            "safe": len(blockers) == 0,
            "warnings": warnings,
            "blockers": blockers,
            "snapshot": snapshot
        }

    # IBKR paper environment
    if default_broker == "ibkr" and ibkr_mode == "paper":
        if ibkr_port != 7497:
            warnings.append("IBKR paper mode usually uses port 7497.")

        if execution_mode == "BROKER_PAPER" and ibkr_read_only is True and ibkr_enable_orders is False:
            status = "IBKR_PAPER_READ_ONLY"
            message = "IBKR paper mode is configured in read-only/monitoring mode."

        elif execution_mode == "BROKER_PAPER" and ibkr_read_only is False and ibkr_enable_orders is True:
            status = "IBKR_PAPER_ORDER_TEST"
            message = "IBKR paper order testing is enabled. This can submit paper orders only."

        else:
            status = "MISCONFIGURED"
            message = "IBKR paper settings are inconsistent."

        if allow_live or live_enabled:
            blockers.append("Live trading flags must remain False during IBKR paper mode.")

        return {
            "status": status,
            "message": message,
            "safe": len(blockers) == 0 and status != "MISCONFIGURED",
            "warnings": warnings,
            "blockers": blockers,
            "snapshot": snapshot
        }

    # IBKR live environment
    if default_broker == "ibkr" and ibkr_mode == "live":
        if ibkr_port != 7496:
            warnings.append("IBKR live TWS usually uses port 7496.")

        if ibkr_read_only is True and ibkr_enable_orders is False and allow_live is False and live_enabled is False:
            status = "IBKR_LIVE_READ_ONLY"
            message = "IBKR live is configured for read-only access only. No orders should be possible."

        elif ibkr_read_only is False or ibkr_enable_orders is True or allow_live is True or live_enabled is True:
            status = "IBKR_LIVE_DANGEROUS"
            message = "IBKR live configuration has one or more order/live flags enabled."
            blockers.append("Live environment has dangerous settings. Review immediately.")

        else:
            status = "MISCONFIGURED"
            message = "IBKR live settings are inconsistent."

        return {
            "status": status,
            "message": message,
            "safe": status == "IBKR_LIVE_READ_ONLY" and len(blockers) == 0,
            "warnings": warnings,
            "blockers": blockers,
            "snapshot": snapshot
        }

    return {
        "status": "MISCONFIGURED",
        "message": "Broker environment could not be classified.",
        "safe": False,
        "warnings": warnings,
        "blockers": blockers + ["Unknown broker/environment combination."],
        "snapshot": snapshot
    }


def get_environment_recommendation():
    """
    Return practical recommendation based on current environment.
    """

    result = classify_broker_environment()
    status = result["status"]

    if status == "SAFE_PAPER":
        recommendation = "Safe for local simulated testing."
    elif status == "IBKR_PAPER_READ_ONLY":
        recommendation = "Safe for reading IBKR paper account/positions. Paper orders are disabled."
    elif status == "IBKR_PAPER_ORDER_TEST":
        recommendation = "Allowed only when deliberately testing IBKR paper orders. Return to read-only after testing."
    elif status == "IBKR_LIVE_READ_ONLY":
        recommendation = "Allowed only for live read-only account inspection. Do not enable orders."
    elif status == "IBKR_LIVE_DANGEROUS":
        recommendation = "Stop. Disable live/order flags immediately before continuing."
    else:
        recommendation = "Fix configuration before continuing."

    result["recommendation"] = recommendation

    return result
