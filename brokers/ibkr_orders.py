
"""
IBKR Order Builder

This module creates IBKR order objects safely.

Initial supported scope:
- BUY
- SELL
- Market orders
- Limit orders

No order submission happens here.
This file only builds order objects.
"""

from ib_insync import MarketOrder, LimitOrder


SUPPORTED_SIDES = ["BUY", "SELL"]
SUPPORTED_ORDER_TYPES = ["MKT", "LMT"]


def normalize_side(side):
    """
    Normalize order side.
    """

    if side is None:
        raise ValueError("Order side cannot be None.")

    side = str(side).strip().upper()

    if side not in SUPPORTED_SIDES:
        raise ValueError(
            f"Unsupported order side: {side}. "
            f"Supported sides: {SUPPORTED_SIDES}"
        )

    return side


def normalize_order_type(order_type):
    """
    Normalize IBKR order type.
    """

    if order_type is None:
        raise ValueError("Order type cannot be None.")

    order_type = str(order_type).strip().upper()

    aliases = {
        "MARKET": "MKT",
        "MKT": "MKT",
        "LIMIT": "LMT",
        "LMT": "LMT"
    }

    if order_type not in aliases:
        raise ValueError(
            f"Unsupported order type: {order_type}. "
            f"Supported order types: {SUPPORTED_ORDER_TYPES}"
        )

    return aliases[order_type]


def validate_quantity(quantity):
    """
    Validate order quantity.
    """

    try:
        quantity = float(quantity)
    except Exception:
        raise ValueError("Quantity must be numeric.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    return quantity


def validate_limit_price(limit_price):
    """
    Validate limit price.
    """

    try:
        limit_price = float(limit_price)
    except Exception:
        raise ValueError("Limit price must be numeric.")

    if limit_price <= 0:
        raise ValueError("Limit price must be greater than zero.")

    return limit_price


def build_market_order(side, quantity):
    """
    Build an IBKR market order object.

    This does not submit the order.
    """

    side = normalize_side(side)
    quantity = validate_quantity(quantity)

    return MarketOrder(
        action=side,
        totalQuantity=quantity
    )


def build_limit_order(side, quantity, limit_price):
    """
    Build an IBKR limit order object.

    This does not submit the order.
    """

    side = normalize_side(side)
    quantity = validate_quantity(quantity)
    limit_price = validate_limit_price(limit_price)

    return LimitOrder(
        action=side,
        totalQuantity=quantity,
        lmtPrice=limit_price
    )


def build_order(
    side,
    quantity,
    order_type="LMT",
    limit_price=None
):
    """
    Build an IBKR order object.

    Supported:
    - MKT
    - LMT
    """

    order_type = normalize_order_type(order_type)

    if order_type == "MKT":
        return build_market_order(
            side=side,
            quantity=quantity
        )

    if order_type == "LMT":
        if limit_price is None:
            raise ValueError("limit_price is required for limit orders.")

        return build_limit_order(
            side=side,
            quantity=quantity,
            limit_price=limit_price
        )

    raise ValueError(f"Unhandled order type: {order_type}")


def describe_order(order):
    """
    Return a simple dictionary description of an IBKR order object.
    """

    return {
        "action": getattr(order, "action", None),
        "orderType": getattr(order, "orderType", None),
        "totalQuantity": getattr(order, "totalQuantity", None),
        "lmtPrice": getattr(order, "lmtPrice", None),
        "tif": getattr(order, "tif", None)
    }


def build_order_from_request(order_request):
    """
    Build an order from a request dictionary.

    Example:
        {
            "side": "BUY",
            "quantity": 1,
            "order_type": "LMT",
            "limit_price": 500
        }
    """

    side = order_request.get("side")
    quantity = order_request.get("quantity")
    order_type = order_request.get("order_type", "LMT")
    limit_price = order_request.get("limit_price")

    return build_order(
        side=side,
        quantity=quantity,
        order_type=order_type,
        limit_price=limit_price
    )
