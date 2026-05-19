
"""
IBKR Order Builder Test

This test does not connect to IBKR.
It only confirms that order objects can be created safely.
No orders are submitted.
"""

import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent
BROKERS_PATH = PROJECT_PATH / "brokers"

if str(BROKERS_PATH) not in sys.path:
    sys.path.append(str(BROKERS_PATH))

from ibkr_orders import (
    build_market_order,
    build_limit_order,
    build_order,
    build_order_from_request,
    describe_order
)


def main():
    print("IBKR Order Builder Test")
    print("=======================")

    print("\nMarket order test:")
    market_order = build_market_order(
        side="BUY",
        quantity=1
    )

    print(describe_order(market_order))

    print("\nLimit order test:")
    limit_order = build_limit_order(
        side="BUY",
        quantity=1,
        limit_price=500
    )

    print(describe_order(limit_order))

    print("\nGeneric order builder test:")
    generic_order = build_order(
        side="SELL",
        quantity=2,
        order_type="LMT",
        limit_price=505
    )

    print(describe_order(generic_order))

    print("\nOrder request test:")
    order_request = {
        "side": "BUY",
        "quantity": 1,
        "order_type": "LMT",
        "limit_price": 500
    }

    request_order = build_order_from_request(order_request)

    print(describe_order(request_order))

    print("\nInvalid side test:")

    try:
        build_order(
            side="SHORT",
            quantity=1,
            order_type="MKT"
        )
    except Exception as e:
        print("Blocked correctly:")
        print(type(e).__name__)
        print(e)

    print("\nInvalid limit order test:")

    try:
        build_order(
            side="BUY",
            quantity=1,
            order_type="LMT"
        )
    except Exception as e:
        print("Blocked correctly:")
        print(type(e).__name__)
        print(e)

    print("\nOrder builder test completed.")
    print("No broker connection was attempted.")
    print("No orders were submitted.")


if __name__ == "__main__":
    main()
