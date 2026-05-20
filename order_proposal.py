
"""
Order Proposal Builder

This module converts a strategy signal into a proposed broker order.

It does not submit orders.
It does not connect to IBKR.
It only prepares a proposed order for review.
"""

from datetime import datetime
import math


ACTIONABLE_SIGNALS = ["BUY", "SELL"]


def normalize_signal_action(action):
    """
    Normalize a signal action.
    """

    if action is None:
        raise ValueError("Signal action cannot be None.")

    action = str(action).strip().upper()

    valid_actions = [
        "BUY",
        "SELL",
        "HOLD",
        "STAY IN CASH"
    ]

    if action not in valid_actions:
        raise ValueError(
            f"Unsupported signal action: {action}. "
            f"Valid actions: {valid_actions}"
        )

    return action


def calculate_order_quantity(
    account_equity,
    position_size,
    estimated_price,
    allow_fractional=False
):
    """
    Calculate order quantity from account equity, position size, and estimated price.

    Example:
        account_equity = 10000
        position_size = 0.05
        estimated_price = 500

        order_value = 500
        quantity = 1
    """

    try:
        account_equity = float(account_equity)
        position_size = float(position_size)
        estimated_price = float(estimated_price)
    except Exception:
        raise ValueError("account_equity, position_size, and estimated_price must be numeric.")

    if account_equity <= 0:
        raise ValueError("account_equity must be greater than zero.")

    if position_size <= 0:
        raise ValueError("position_size must be greater than zero.")

    if position_size > 1:
        raise ValueError("position_size cannot be greater than 1.0.")

    if estimated_price <= 0:
        raise ValueError("estimated_price must be greater than zero.")

    target_order_value = account_equity * position_size

    if allow_fractional:
        quantity = target_order_value / estimated_price
    else:
        quantity = math.floor(target_order_value / estimated_price)

    if quantity <= 0:
        return {
            "quantity": 0,
            "target_order_value": target_order_value,
            "estimated_order_value": 0,
            "reason": "Calculated quantity is zero. Position size may be too small for this asset price."
        }

    estimated_order_value = quantity * estimated_price

    return {
        "quantity": quantity,
        "target_order_value": target_order_value,
        "estimated_order_value": estimated_order_value,
        "reason": "Quantity calculated successfully."
    }


def build_order_proposal_from_signal(
    signal_result,
    account_equity=10000,
    position_size=0.01,
    order_type="LMT",
    limit_price=None,
    allow_fractional=False,
    current_position_quantity=0,
    asset_type="etf",
    broker_name="ibkr",
    execution_mode="BROKER_PAPER"
):
    """
    Convert signal result into a proposed order.

    signal_result example:
        {
            "action": "BUY",
            "ticker": "SPY",
            "latest_close": 500,
            "strategy_label": "Moving Average 20/50"
        }
    """

    if not isinstance(signal_result, dict):
        raise ValueError("signal_result must be a dictionary.")

    action = normalize_signal_action(signal_result.get("action"))

    ticker = str(signal_result.get("ticker", "")).strip().upper()

    if not ticker:
        raise ValueError("signal_result must contain ticker.")

    latest_close = signal_result.get("latest_close")

    if latest_close is None:
        raise ValueError("signal_result must contain latest_close.")

    latest_close = float(latest_close)

    strategy_label = signal_result.get("strategy_label", "")
    signal_reason = signal_result.get("reason", "")

    if action not in ACTIONABLE_SIGNALS:
        return {
            "actionable": False,
            "proposal_status": "no_order",
            "reason": f"No order proposed because signal action is {action}.",
            "signal_action": action,
            "ticker": ticker,
            "strategy_label": strategy_label,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    side = action

    if order_type is None:
        order_type = "LMT"

    order_type = str(order_type).strip().upper()

    if order_type not in ["LMT", "MKT"]:
        raise ValueError("order_type must be LMT or MKT.")

    if order_type == "LMT":
        if limit_price is None:
            limit_price = latest_close

        limit_price = float(limit_price)

        if limit_price <= 0:
            raise ValueError("limit_price must be greater than zero.")

        estimated_price = limit_price

    else:
        estimated_price = latest_close
        limit_price = None

    quantity_result = calculate_order_quantity(
        account_equity=account_equity,
        position_size=position_size,
        estimated_price=estimated_price,
        allow_fractional=allow_fractional
    )

    quantity = quantity_result["quantity"]

    if quantity <= 0:
        return {
            "actionable": False,
            "proposal_status": "blocked_quantity_zero",
            "reason": quantity_result["reason"],
            "signal_action": action,
            "ticker": ticker,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "limit_price": limit_price,
            "estimated_price": estimated_price,
            "account_equity": account_equity,
            "position_size": position_size,
            "strategy_label": strategy_label,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    if side == "SELL":
        if current_position_quantity <= 0:
            return {
                "actionable": False,
                "proposal_status": "blocked_no_position_to_sell",
                "reason": "SELL signal received, but current_position_quantity is zero. Short selling is not allowed.",
                "signal_action": action,
                "ticker": ticker,
                "side": side,
                "quantity": quantity,
                "order_type": order_type,
                "limit_price": limit_price,
                "estimated_price": estimated_price,
                "current_position_quantity": current_position_quantity,
                "strategy_label": strategy_label,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        quantity = min(quantity, current_position_quantity)

    proposal = {
        "actionable": True,
        "proposal_status": "proposed",
        "reason": "Order proposal created from signal.",
        "signal_action": action,
        "signal_reason": signal_reason,
        "ticker": ticker,
        "side": side,
        "quantity": quantity,
        "order_type": order_type,
        "limit_price": limit_price,
        "estimated_price": estimated_price,
        "target_order_value": quantity_result["target_order_value"],
        "estimated_order_value": quantity * estimated_price,
        "account_equity": account_equity,
        "position_size": position_size,
        "allow_fractional": allow_fractional,
        "current_position_quantity": current_position_quantity,
        "asset_type": asset_type,
        "broker_name": broker_name,
        "execution_mode": execution_mode,
        "strategy_label": strategy_label,
        "latest_signal_date": signal_result.get("latest_date"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return proposal


def proposal_to_order_request(proposal):
    """
    Convert a proposal into a basic order request dictionary.

    This does not submit the order.
    """

    if not proposal.get("actionable", False):
        raise ValueError("Cannot convert a non-actionable proposal into an order request.")

    return {
        "ticker": proposal["ticker"],
        "side": proposal["side"],
        "quantity": proposal["quantity"],
        "order_type": proposal["order_type"],
        "limit_price": proposal["limit_price"],
        "asset_type": proposal["asset_type"],
        "estimated_order_value": proposal["estimated_order_value"],
        "broker_name": proposal["broker_name"],
        "execution_mode": proposal["execution_mode"]
    }
