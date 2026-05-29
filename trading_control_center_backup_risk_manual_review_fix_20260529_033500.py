
"""
Trading Control Center

This module consolidates the main paper trading workflow into one safe sequence.

It does not place orders.
It does not enable live trading.
It prepares and evaluates a trading decision before any broker submission.
"""

from datetime import datetime
import inspect

from live_signal import generate_live_signal
from order_proposal import build_order_proposal_from_signal
from broker_account_snapshot import get_broker_account_snapshot
from market_hours import should_allow_market_order_workflow
from position_aware_execution import evaluate_position_aware_proposal_with_snapshot
from duplicate_order_guard import check_duplicate_order_from_proposal
from price_validation import validate_order_price_from_proposal
from risk_manager import create_risk_manager_from_config
from safety_manager import read_emergency_stop_state
from broker_environment import get_environment_recommendation
from trading_database import insert_trading_control_center_run


def run_trading_control_center_check(
    ticker="SPY",
    strategy_name="moving_average",
    short_window=20,
    long_window=50,
    quantity=1,
    order_type="LMT",
    limit_price=None,
    paper_broker=None,
    allow_after_hours=False,
    allow_short_selling=False,
    allow_add_to_existing=False,
    manual_reference_price=None,
):
    """
    Run the full pre-trade decision workflow.

    This function does not submit any order.
    """

    ticker = str(ticker or "SPY").strip().upper()
    order_type = str(order_type or "LMT").strip().upper()

    result = {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ticker": ticker,
        "strategy_name": strategy_name,
        "submitted_to_broker": False,
        "workflow_steps": {},
        "blockers": [],
        "warnings": [],
        "final_decision": "blocked",
        "final_message": "",
    }

    # 1. Broker environment
    try:
        broker_env = get_environment_recommendation()
        result["workflow_steps"]["broker_environment"] = broker_env

        if not broker_env.get("safe", False):
            result["warnings"].append("Broker environment is not fully marked safe. Review environment panel.")
    except Exception as e:
        result["workflow_steps"]["broker_environment"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Could not evaluate broker environment.")

    # 2. Emergency stop
    try:
        emergency_state = read_emergency_stop_state()
        result["workflow_steps"]["emergency_stop"] = emergency_state

        if emergency_state.get("active", False):
            result["blockers"].append("Emergency stop is active.")
    except Exception as e:
        result["workflow_steps"]["emergency_stop"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Could not read emergency stop state.")

    # 3. Generate signal
    try:
        signal_result, signal_data, signal_summary, signal_trade_log = generate_live_signal(
            ticker=ticker,
            strategy_name=strategy_name,
            short_window=short_window,
            long_window=long_window,
        )

        result["workflow_steps"]["signal"] = signal_result
        result["workflow_steps"]["signal_summary"] = signal_summary

        if not signal_result.get("actionable", False):
            result["blockers"].append(
                f"Signal is not actionable: {signal_result.get('action') or signal_result.get('signal_action')}"
            )

    except Exception as e:
        result["workflow_steps"]["signal"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Signal generation failed.")
        return finalize_control_center_result(result)

    # 4. Build order proposal
    try:
        proposal_signature = inspect.signature(build_order_proposal_from_signal)

        possible_kwargs = {
            "signal_result": signal_result,
            "signal": signal_result,
            "latest_signal": signal_result,
            "quantity": quantity,
            "order_quantity": quantity,
            "shares": quantity,
            "order_type": order_type,
            "limit_price": limit_price,
        }

        accepted_kwargs = {
            key: value
            for key, value in possible_kwargs.items()
            if key in proposal_signature.parameters
        }

        try:
            proposal = build_order_proposal_from_signal(**accepted_kwargs)
        except TypeError:
            proposal = build_order_proposal_from_signal(signal_result)

        if not isinstance(proposal, dict):
            proposal = {
                "ticker": ticker,
                "side": signal_result.get("action") or signal_result.get("signal_action"),
                "quantity": quantity,
                "order_type": order_type,
                "limit_price": limit_price,
                "actionable": False,
                "proposal_status": "invalid",
                "reason": "build_order_proposal_from_signal did not return a dictionary."
            }

        proposal.setdefault("ticker", ticker)
        proposal.setdefault("order_type", order_type)

        # Trading Control Center manual quantity override:
        # If the proposal engine calculates 0 shares because position size is too small,
        # use the manually entered dashboard quantity instead.
        try:
            proposal_quantity = float(proposal.get("quantity", 0) or 0)
        except Exception:
            proposal_quantity = 0

        try:
            manual_quantity = float(quantity or 0)
        except Exception:
            manual_quantity = 0

        if proposal_quantity <= 0 and manual_quantity > 0:
            proposal["quantity"] = manual_quantity
            proposal["actionable"] = True
            proposal["proposal_status"] = "manual_quantity_override"
            proposal["reason"] = (
                "Proposal quantity was zero, so Trading Control Center manual quantity was used."
            )
        else:
            proposal.setdefault("quantity", quantity)

        if limit_price is not None:
            proposal.setdefault("limit_price", limit_price)

        if "side" not in proposal or not proposal.get("side"):
            signal_action = (
                signal_result.get("action")
                or signal_result.get("signal_action")
                or signal_result.get("recommended_order_side")
            )

            if signal_action:
                proposal["side"] = str(signal_action).upper()

        if "actionable" not in proposal:
            proposal["actionable"] = proposal.get("side") in ["BUY", "SELL"]

        result["workflow_steps"]["order_proposal"] = proposal

        if not proposal.get("actionable", False):
            result["blockers"].append("Order proposal is not actionable.")

    except Exception as e:
        result["workflow_steps"]["order_proposal"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Order proposal generation failed.")
        return finalize_control_center_result(result)

    # 5. Account snapshot
    try:
        snapshot = get_broker_account_snapshot(paper_broker=paper_broker)
        result["workflow_steps"]["account_snapshot"] = snapshot

        if not snapshot.get("snapshot_available", False):
            result["warnings"].append("Account snapshot is not available.")
    except Exception as e:
        result["workflow_steps"]["account_snapshot"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["warnings"].append("Could not capture account snapshot.")
        snapshot = {}

    # 6. Market hours
    try:
        market_hours = should_allow_market_order_workflow(
            market="US",
            allow_after_hours=allow_after_hours
        )

        result["workflow_steps"]["market_hours"] = market_hours

        if not market_hours.get("allowed", False):
            result["blockers"].append(market_hours.get("reason", "Market-hours workflow blocked."))

    except Exception as e:
        result["workflow_steps"]["market_hours"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Market-hours check failed.")

    # 7. Position-aware check
    try:
        position_check = evaluate_position_aware_proposal_with_snapshot(
            proposal=proposal,
            account_snapshot=snapshot,
            allow_short_selling=allow_short_selling,
            allow_add_to_existing=allow_add_to_existing
        )

        result["workflow_steps"]["position_aware"] = position_check

        if not position_check.get("allowed", False):
            result["blockers"].extend(position_check.get("blockers", []))

        result["warnings"].extend(position_check.get("warnings", []))

    except Exception as e:
        result["workflow_steps"]["position_aware"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Position-aware check failed.")

    # 8. Duplicate-order guard
    try:
        duplicate_check = check_duplicate_order_from_proposal(
            proposal=proposal,
            signal_id=None,
            lookback_minutes=1440
        )

        result["workflow_steps"]["duplicate_order"] = duplicate_check

        if duplicate_check.get("duplicate_blocked", False):
            result["blockers"].extend(duplicate_check.get("blockers", []))

        result["warnings"].extend(duplicate_check.get("warnings", []))

    except Exception as e:
        result["workflow_steps"]["duplicate_order"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Duplicate-order check failed.")

    # 9. Price validation
    try:
        price_check = validate_order_price_from_proposal(
            proposal=proposal,
            signal=signal_result,
            account_snapshot=snapshot,
            manual_reference_price=manual_reference_price,
            max_buy_premium_pct=0.02,
            max_sell_discount_pct=0.02
        )

        result["workflow_steps"]["price_validation"] = price_check

        if not price_check.get("allowed", False):
            result["blockers"].extend(price_check.get("blockers", []))

        result["warnings"].extend(price_check.get("warnings", []))

    except Exception as e:
        result["workflow_steps"]["price_validation"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Price validation failed.")

    # 10. Risk manager
    try:
        risk_manager = create_risk_manager_from_config()

        estimated_price = proposal.get("limit_price") or proposal.get("latest_price") or signal_result.get("latest_close")
        estimated_order_value = None

        if estimated_price is not None:
            try:
                estimated_order_value = float(quantity) * float(estimated_price)
            except Exception:
                estimated_order_value = None

        risk_result = risk_manager.approve_broker_order(
            ticker=proposal.get("ticker"),
            side=proposal.get("side"),
            quantity=proposal.get("quantity"),
            order_type=proposal.get("order_type"),
            asset_type=proposal.get("asset_type", "etf"),
            proposed_position_size=proposal.get("proposed_position_size", 0.01),
            estimated_price=estimated_price,
            estimated_order_value=estimated_order_value,
            current_position_quantity=0,
            manual_confirmation_given=False,
            broker_name="ibkr",
            execution_mode="BROKER_PAPER",
            live_order=False
        )

        risk_payload = {
            "approved": risk_result.approved,
            "reason": risk_result.reason,
            "details": risk_result.details,
        }

        result["workflow_steps"]["risk_manager"] = risk_payload

        if not risk_result.approved:
            result["blockers"].append(f"Risk manager blocked order: {risk_result.reason}")

    except Exception as e:
        result["workflow_steps"]["risk_manager"] = {
            "error": f"{type(e).__name__}: {e}"
        }
        result["blockers"].append("Risk manager check failed.")

    return finalize_control_center_result(result)


def finalize_control_center_result(result):
    """
    Finalize decision summary.
    """

    blockers = result.get("blockers", [])

    # Remove duplicated blockers while preserving order.
    cleaned_blockers = []
    for item in blockers:
        if item and item not in cleaned_blockers:
            cleaned_blockers.append(item)

    warnings = result.get("warnings", [])
    cleaned_warnings = []
    for item in warnings:
        if item and item not in cleaned_warnings:
            cleaned_warnings.append(item)

    result["blockers"] = cleaned_blockers
    result["warnings"] = cleaned_warnings

    if cleaned_blockers:
        result["final_decision"] = "blocked"
        result["final_message"] = "Trading workflow is blocked. Review blockers before any broker submission."
    else:
        result["final_decision"] = "ready_for_manual_paper_review"
        result["final_message"] = (
            "Pre-trade checks passed. This does not submit an order. "
            "Manual confirmation and paper-only execution should still be required."
        )

    try:
        run_id = insert_trading_control_center_run(result)
        result["database_logged"] = True
        result["database_run_id"] = run_id
    except Exception as db_error:
        result["database_logged"] = False
        result["database_error"] = f"{type(db_error).__name__}: {db_error}"

    return result


def get_control_center_step_summary(control_result):
    """
    Return compact pass/fail summary of workflow steps.
    """

    steps = control_result.get("workflow_steps", {})

    rows = []

    for step_name, payload in steps.items():
        ok = True
        note = ""

        if isinstance(payload, dict):
            if "error" in payload:
                ok = False
                note = payload.get("error", "")
            elif payload.get("allowed") is False:
                ok = False
                note = payload.get("reason", "")
            elif payload.get("duplicate_blocked") is True:
                ok = False
                note = "Duplicate order blocked."
            elif payload.get("approved") is False:
                ok = False
                note = payload.get("reason", "")
            elif payload.get("actionable") is False and step_name in ["signal", "order_proposal"]:
                ok = False
                note = "Not actionable."
        else:
            note = "Non-dict result."

        rows.append({
            "step": step_name,
            "ok": ok,
            "note": note,
        })

    return rows
