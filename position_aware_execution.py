
"""
Position-Aware Signal Execution

This module checks current positions before allowing a signal to become an order.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from datetime import datetime


def normalize_action(action):
    if action is None:
        return "UNKNOWN"

    return str(action).strip().upper()


def normalize_ticker(ticker):
    if ticker is None:
        return ""

    return str(ticker).strip().upper()


def extract_position_quantity(positions, ticker):
    """
    Extract current position quantity for ticker from a list or dict of positions.
    """

    ticker = normalize_ticker(ticker)

    if not positions:
        return 0.0

    # Dict format: {"SPY": {"quantity": 1}}
    if isinstance(positions, dict):
        position = positions.get(ticker)

        if position is None:
            return 0.0

        if isinstance(position, dict):
            return float(
                position.get("quantity")
                or position.get("position")
                or position.get("shares")
                or 0.0
            )

        try:
            return float(position)
        except Exception:
            return 0.0

    # List format: [{"ticker": "SPY", "quantity": 1}]
    if isinstance(positions, list):
        for position in positions:
            if not isinstance(position, dict):
                continue

            position_ticker = normalize_ticker(
                position.get("ticker")
                or position.get("symbol")
            )

            if position_ticker == ticker:
                return float(
                    position.get("quantity")
                    or position.get("position")
                    or position.get("shares")
                    or 0.0
                )

    return 0.0


def classify_position_state(quantity):
    """
    Classify current position state.
    """

    quantity = float(quantity or 0)

    if quantity > 0:
        return "long"
    elif quantity < 0:
        return "short"
    else:
        return "flat"


def evaluate_position_aware_signal(
    signal,
    current_positions=None,
    allow_short_selling=False,
    allow_add_to_existing=False
):
    """
    Decide whether a signal can become an actionable order based on current position.

    Rules:
    - BUY is allowed only if flat, unless adding to existing positions is allowed.
    - SELL is allowed only if long.
    - HOLD does not create an order.
    - STAY IN CASH does not create an order.
    - Short selling is blocked unless explicitly allowed.
    """

    if not isinstance(signal, dict):
        raise ValueError("signal must be a dictionary.")

    ticker = normalize_ticker(signal.get("ticker"))
    action = normalize_action(signal.get("action"))

    quantity = extract_position_quantity(current_positions or {}, ticker)
    position_state = classify_position_state(quantity)

    blockers = []
    warnings = []
    allowed = False
    recommended_order_side = None
    recommended_action = "no_order"

    if action == "BUY":
        if position_state == "flat":
            allowed = True
            recommended_order_side = "BUY"
            recommended_action = "open_long"
        elif position_state == "long":
            if allow_add_to_existing:
                allowed = True
                recommended_order_side = "BUY"
                recommended_action = "add_to_long"
                warnings.append("Already long. This BUY would add to an existing position.")
            else:
                blockers.append("BUY blocked because a long position already exists.")
        elif position_state == "short":
            blockers.append("BUY signal found while short position exists. Short-covering logic is not enabled.")

    elif action == "SELL":
        if position_state == "long":
            allowed = True
            recommended_order_side = "SELL"
            recommended_action = "close_long"
        elif position_state == "flat":
            blockers.append("SELL blocked because there is no position to sell.")
        elif position_state == "short":
            if allow_short_selling:
                warnings.append("Already short. SELL may increase short exposure.")
                allowed = True
                recommended_order_side = "SELL"
                recommended_action = "add_to_short"
            else:
                blockers.append("SELL blocked because short selling is not allowed.")

    elif action in ["HOLD", "STAY IN CASH"]:
        allowed = False
        recommended_action = "no_order"
        warnings.append(f"{action} signal does not require an order.")

    else:
        blockers.append(f"Unknown or unsupported signal action: {action}")

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ticker": ticker,
        "signal_action": action,
        "current_quantity": quantity,
        "position_state": position_state,
        "allowed": allowed,
        "actionable": allowed,
        "recommended_order_side": recommended_order_side,
        "recommended_action": recommended_action,
        "blockers": blockers,
        "warnings": warnings,
        "allow_short_selling": allow_short_selling,
        "allow_add_to_existing": allow_add_to_existing,
        "signal": signal,
    }


def evaluate_position_aware_proposal(
    proposal,
    current_positions=None,
    allow_short_selling=False,
    allow_add_to_existing=False
):
    """
    Evaluate an order proposal against current positions.
    """

    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a dictionary.")

    signal_like = {
        "ticker": proposal.get("ticker"),
        "action": proposal.get("side"),
    }

    result = evaluate_position_aware_signal(
        signal=signal_like,
        current_positions=current_positions,
        allow_short_selling=allow_short_selling,
        allow_add_to_existing=allow_add_to_existing
    )

    result["proposal"] = proposal

    return result


def get_positions_from_paper_broker(paper_broker):
    """
    Extract positions from local simulated paper broker.
    """

    if paper_broker is None:
        return {}

    if hasattr(paper_broker, "get_account_info"):
        try:
            account_info = paper_broker.get_account_info()
            return account_info.get("open_positions", [])
        except Exception:
            pass

    return getattr(paper_broker, "positions", {}) or {}


def get_position_aware_status():
    """
    Return static status for dashboard.
    """

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "short_selling_default": False,
        "add_to_existing_default": False,
        "purpose": "Prevent invalid or duplicated position actions before order submission.",
        "rules": [
            "BUY is normally allowed only when flat.",
            "SELL is normally allowed only when long.",
            "HOLD does not create an order.",
            "STAY IN CASH does not create an order.",
            "Short selling is blocked by default.",
            "Adding to existing positions is blocked by default.",
        ]
    }
