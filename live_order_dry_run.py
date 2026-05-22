
"""
Live Order Dry Run Mode

This module simulates the final live-order validation process without sending
anything to IBKR.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

PROJECT_PATH = Path(__file__).resolve().parent
BROKERS_PATH = PROJECT_PATH / "brokers"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(BROKERS_PATH) not in sys.path:
    sys.path.append(str(BROKERS_PATH))


def ensure_streamlit_event_loop():
    """
    Ensure an asyncio event loop exists in the current thread.

    Streamlit runs app code inside ScriptRunner.scriptThread.
    ib_insync/eventkit expects an event loop to exist.
    """

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())


from risk_manager import create_risk_manager_from_config
from safety_manager import read_emergency_stop_state
from live_mode_lock import evaluate_live_mode_lock
from live_warning import read_warning_state


def run_live_order_dry_run(
    ticker,
    side,
    quantity,
    order_type="LMT",
    limit_price=None,
    asset_type="etf",
    proposed_position_size=0.01,
    estimated_price=None,
    estimated_order_value=None,
    current_position_quantity=0,
    manual_confirmation_given=False,
    strategy_name=None,
    signal=None
):
    """
    Perform a dry run for a future live order.

    This function:
    - builds the IBKR contract object
    - builds the IBKR order object
    - checks emergency stop
    - checks live warning acknowledgement
    - checks live mode lock
    - checks risk manager
    - returns a dry-run report

    It does not connect to IBKR.
    It does not submit any order.
    """

    ensure_streamlit_event_loop()

    # Import IBKR builders lazily after event loop exists
    from ibkr_contracts import build_us_stock_contract, describe_contract
    from ibkr_orders import build_order, describe_order

    from config import EXECUTION_MODE, DEFAULT_BROKER

    ticker = str(ticker).strip().upper()
    side = str(side).strip().upper()
    order_type = str(order_type).strip().upper()

    if estimated_price is None:
        estimated_price = limit_price

    if estimated_order_value is None and estimated_price is not None:
        estimated_order_value = float(quantity) * float(estimated_price)

    dry_run_report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dry_run": True,
        "submitted_to_broker": False,
        "ticker": ticker,
        "side": side,
        "quantity": quantity,
        "order_type": order_type,
        "limit_price": limit_price,
        "asset_type": asset_type,
        "strategy_name": strategy_name,
        "signal": signal,
        "execution_mode": EXECUTION_MODE,
        "default_broker": DEFAULT_BROKER,
    }

    try:
        contract = build_us_stock_contract(ticker)
        contract_description = describe_contract(contract)

        dry_run_report["contract_valid"] = True
        dry_run_report["contract"] = contract_description

    except Exception as e:
        dry_run_report["contract_valid"] = False
        dry_run_report["contract_error"] = str(e)
        dry_run_report["dry_run_passed"] = False
        dry_run_report["recommendation"] = "Dry run failed because contract could not be built."
        return dry_run_report

    try:
        order = build_order(
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price
        )

        order_description = describe_order(order)

        dry_run_report["order_valid"] = True
        dry_run_report["order"] = order_description

    except Exception as e:
        dry_run_report["order_valid"] = False
        dry_run_report["order_error"] = str(e)
        dry_run_report["dry_run_passed"] = False
        dry_run_report["recommendation"] = "Dry run failed because order could not be built."
        return dry_run_report

    emergency_state = read_emergency_stop_state()
    warning_state = read_warning_state()
    live_lock_eval = evaluate_live_mode_lock()

    dry_run_report["emergency_stop"] = emergency_state
    dry_run_report["live_warning"] = {
        "acknowledged": warning_state.get("acknowledged", False),
        "acknowledged_at": warning_state.get("acknowledged_at", ""),
        "acknowledged_by": warning_state.get("acknowledged_by", "")
    }
    dry_run_report["live_mode_lock"] = {
        "status": live_lock_eval.get("status"),
        "live_mode_allowed": live_lock_eval.get("live_mode_allowed"),
        "failed_checks": live_lock_eval.get("failed_checks", []),
        "passed_checks": live_lock_eval.get("passed_checks", [])
    }

    risk_manager = create_risk_manager_from_config()

    risk_result = risk_manager.approve_broker_order(
        ticker=ticker,
        side=side,
        quantity=quantity,
        order_type=order_type,
        asset_type=asset_type,
        proposed_position_size=proposed_position_size,
        estimated_price=estimated_price,
        estimated_order_value=estimated_order_value,
        current_position_quantity=current_position_quantity,
        manual_confirmation_given=manual_confirmation_given,
        broker_name="ibkr",
        execution_mode="LIVE_MANUAL",
        live_order=True
    )

    dry_run_report["risk_check"] = {
        "approved": risk_result.approved,
        "reason": risk_result.reason,
        "details": risk_result.details
    }

    blockers = []

    if emergency_state.get("active", False):
        blockers.append("Emergency stop is active.")

    if not warning_state.get("acknowledged", False):
        blockers.append("Live warning has not been acknowledged.")

    if not live_lock_eval.get("live_mode_allowed", False):
        blockers.append("Live mode lock is not unlocked.")

    if not risk_result.approved:
        blockers.append(f"Risk manager blocked order: {risk_result.reason}")

    if not manual_confirmation_given:
        blockers.append("Manual confirmation was not given.")

    dry_run_report["blockers"] = blockers

    dry_run_passed = len(blockers) == 0

    dry_run_report["dry_run_passed"] = dry_run_passed

    if dry_run_passed:
        dry_run_report["recommendation"] = (
            "Dry run passed. This only means the order structure and safety gates passed. "
            "It does not submit the order and does not authorize automatic trading."
        )
    else:
        dry_run_report["recommendation"] = (
            "Dry run blocked. Do not attempt live order submission until all blockers are resolved."
        )

    return dry_run_report
