
"""
IBKR Contract Builder Test

This test does not connect to IBKR.
It only confirms that contract objects can be created safely.
"""

import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent
BROKERS_PATH = PROJECT_PATH / "brokers"

if str(BROKERS_PATH) not in sys.path:
    sys.path.append(str(BROKERS_PATH))

from ibkr_contracts import (
    build_us_stock_contract,
    describe_contract,
    build_contract_from_order_request
)


def main():
    print("IBKR Contract Builder Test")
    print("==========================")

    test_symbols = [
        "SPY",
        "QQQ",
        "AAPL",
        "MSFT"
    ]

    for symbol in test_symbols:
        contract = build_us_stock_contract(symbol)
        description = describe_contract(contract)

        print(symbol, "->", description)

    print("\nTesting contract from order request...")

    order_request = {
        "ticker": "SPY",
        "asset_type": "etf",
        "exchange": "SMART",
        "currency": "USD"
    }

    contract = build_contract_from_order_request(order_request)

    print("Order request contract:", describe_contract(contract))

    print("\nTesting blocked symbol...")

    try:
        build_us_stock_contract("TSLA")
    except Exception as e:
        print("Blocked correctly:")
        print(type(e).__name__)
        print(e)

    print("\nContract builder test completed.")
    print("No broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
