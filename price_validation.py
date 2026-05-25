
"""
Real Price Validation Layer

This module validates proposed order prices against available reference prices.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from datetime import datetime


def safe_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def get_reference_price_from_sources(
    ticker,
    proposal=None,
    signal=None,
    account_snapshot=None,
    manual_reference_price=None
):
    """
    Try to find the best available reference price.

    Priority:
    1. Manual reference price
    2. Proposal latest_price / limit_price
    3. Signal latest_close
    4. Account snapshot position latest_price
    """

    ticker = str(ticker or "").upper().strip()

    if manual_reference_price is not None:
        price = safe_float(manual_reference_price)
        if price is not None and price > 0:
            return {
                "reference_price": price,
                "source": "manual_reference_price",
                "available": True,
            }

    if isinstance(proposal, dict):
        for key in ["latest_price", "reference_price", "market_price"]:
            price = safe_float(proposal.get(key))
            if price is not None and price > 0:
                return {
                    "reference_price": price,
                    "source": f"proposal.{key}",
                    "available": True,
                }

    if isinstance(signal, dict):
        for key in ["latest_close", "latest_price", "reference_price"]:
            price = safe_float(signal.get(key))
            if price is not None and price > 0:
                return {
                    "reference_price": price,
                    "source": f"signal.{key}",
                    "available": True,
                }

    if isinstance(account_snapshot, dict):
        positions = account_snapshot.get("positions", [])

        if isinstance(positions, list):
            for position in positions:
                if not isinstance(position, dict):
                    continue

                position_ticker = str(
                    position.get("ticker") or position.get("symbol") or ""
                ).upper().strip()

                if position_ticker == ticker:
                    price = safe_float(
                        position.get("latest_price")
                        or position.get("market_price")
                        or position.get("avg_price")
                    )

                    if price is not None and price > 0:
                        return {
                            "reference_price": price,
                            "source": "account_snapshot.position_price",
                            "available": True,
                        }

    if isinstance(proposal, dict):
        price = safe_float(proposal.get("limit_price"))
        if price is not None and price > 0:
            return {
                "reference_price": price,
                "source": "proposal.limit_price_fallback",
                "available": True,
            }

    return {
        "reference_price": None,
        "source": None,
        "available": False,
    }


def validate_order_price(
    ticker,
    side,
    order_type,
    limit_price=None,
    proposal=None,
    signal=None,
    account_snapshot=None,
    manual_reference_price=None,
    max_buy_premium_pct=0.02,
    max_sell_discount_pct=0.02,
    allow_unpriced_market_order=False,
    allow_deep_test_limit_price=True
):
    """
    Validate order price against a reference price.

    Rules:
    - MKT orders require a reference price unless explicitly allowed.
    - BUY LMT should not be too far above reference price.
    - SELL LMT should not be too far below reference price.
    - Very low BUY test prices can be allowed in paper mode as non-fill tests.
    """

    ticker = str(ticker or "").upper().strip()
    side = str(side or "").upper().strip()
    order_type = str(order_type or "").upper().strip()

    limit_price_value = safe_float(limit_price)

    reference_result = get_reference_price_from_sources(
        ticker=ticker,
        proposal=proposal,
        signal=signal,
        account_snapshot=account_snapshot,
        manual_reference_price=manual_reference_price
    )

    reference_price = reference_result.get("reference_price")

    blockers = []
    warnings = []

    if not ticker:
        blockers.append("Ticker is missing.")

    if side not in ["BUY", "SELL"]:
        blockers.append(f"Unsupported side: {side}")

    if order_type not in ["LMT", "MKT"]:
        blockers.append(f"Unsupported order type: {order_type}")

    if order_type == "LMT":
        if limit_price_value is None or limit_price_value <= 0:
            blockers.append("Limit price must be greater than zero for LMT orders.")

    if not reference_result.get("available"):
        if order_type == "MKT" and allow_unpriced_market_order:
            warnings.append("Reference price unavailable, but unpriced market order was manually allowed.")
        else:
            blockers.append("No reference price available for validation.")

    price_distance_pct = None
    price_status = "unknown"

    if reference_price is not None and reference_price > 0 and limit_price_value is not None:
        price_distance_pct = (limit_price_value - reference_price) / reference_price

        if order_type == "LMT" and side == "BUY":
            if limit_price_value <= reference_price:
                price_status = "buy_limit_at_or_below_reference"
            elif price_distance_pct <= max_buy_premium_pct:
                price_status = "buy_limit_above_reference_within_tolerance"
                warnings.append(
                    f"BUY limit price is above reference by {price_distance_pct:.2%}."
                )
            else:
                blockers.append(
                    f"BUY limit price is too far above reference price: {price_distance_pct:.2%}."
                )

            if allow_deep_test_limit_price and limit_price_value < reference_price * 0.20:
                warnings.append(
                    "BUY limit price is far below reference price. This looks like a paper non-fill test order."
                )

        elif order_type == "LMT" and side == "SELL":
            if limit_price_value >= reference_price:
                price_status = "sell_limit_at_or_above_reference"
            elif abs(price_distance_pct) <= max_sell_discount_pct:
                price_status = "sell_limit_below_reference_within_tolerance"
                warnings.append(
                    f"SELL limit price is below reference by {abs(price_distance_pct):.2%}."
                )
            else:
                blockers.append(
                    f"SELL limit price is too far below reference price: {abs(price_distance_pct):.2%}."
                )

        elif order_type == "MKT":
            price_status = "market_order_reference_available"
            warnings.append("Market order has reference price, but market orders can still fill away from expected price.")

    allowed = len(blockers) == 0

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ticker": ticker,
        "side": side,
        "order_type": order_type,
        "limit_price": limit_price_value,
        "reference_price": reference_price,
        "reference_source": reference_result.get("source"),
        "reference_available": reference_result.get("available"),
        "price_distance_pct": price_distance_pct,
        "price_status": price_status,
        "allowed": allowed,
        "blockers": blockers,
        "warnings": warnings,
        "max_buy_premium_pct": max_buy_premium_pct,
        "max_sell_discount_pct": max_sell_discount_pct,
    }


def validate_order_price_from_proposal(
    proposal,
    signal=None,
    account_snapshot=None,
    manual_reference_price=None,
    max_buy_premium_pct=0.02,
    max_sell_discount_pct=0.02
):
    """
    Validate price using an order proposal dictionary.
    """

    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a dictionary.")

    return validate_order_price(
        ticker=proposal.get("ticker"),
        side=proposal.get("side"),
        order_type=proposal.get("order_type"),
        limit_price=proposal.get("limit_price"),
        proposal=proposal,
        signal=signal,
        account_snapshot=account_snapshot,
        manual_reference_price=manual_reference_price,
        max_buy_premium_pct=max_buy_premium_pct,
        max_sell_discount_pct=max_sell_discount_pct,
    )


def get_price_validation_status():
    """
    Return static status for dashboard.
    """

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "default_max_buy_premium_pct": 0.02,
        "default_max_sell_discount_pct": 0.02,
        "purpose": "Validate order prices against available reference prices before broker workflow.",
        "rules": [
            "BUY LMT should not be too far above reference price.",
            "SELL LMT should not be too far below reference price.",
            "MKT orders should have a reference price warning.",
            "Missing reference price should block order workflow.",
            "Very low BUY limit prices can be treated as paper non-fill test warnings.",
        ]
    }
