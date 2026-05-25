
"""
Price Validation Test

This script tests the real price validation layer.
It does not connect to IBKR.
It does not place orders.
"""

from price_validation import validate_order_price_from_proposal


def main():
    print("Real Price Validation Test")
    print("==========================")

    signal = {
        "ticker": "SPY",
        "latest_close": 500.00,
        "action": "BUY",
    }

    safe_buy = {
        "ticker": "SPY",
        "side": "BUY",
        "order_type": "LMT",
        "limit_price": 499.00,
    }

    expensive_buy = {
        "ticker": "SPY",
        "side": "BUY",
        "order_type": "LMT",
        "limit_price": 530.00,
    }

    safe_sell = {
        "ticker": "SPY",
        "side": "SELL",
        "order_type": "LMT",
        "limit_price": 501.00,
    }

    bad_sell = {
        "ticker": "SPY",
        "side": "SELL",
        "order_type": "LMT",
        "limit_price": 470.00,
    }

    deep_test_buy = {
        "ticker": "SPY",
        "side": "BUY",
        "order_type": "LMT",
        "limit_price": 1.00,
    }

    print("\nSafe BUY:")
    print(validate_order_price_from_proposal(safe_buy, signal=signal))

    print("\nExpensive BUY:")
    print(validate_order_price_from_proposal(expensive_buy, signal=signal))

    print("\nSafe SELL:")
    print(validate_order_price_from_proposal(safe_sell, signal=signal))

    print("\nBad SELL:")
    print(validate_order_price_from_proposal(bad_sell, signal=signal))

    print("\nDeep test BUY:")
    print(validate_order_price_from_proposal(deep_test_buy, signal=signal))

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
