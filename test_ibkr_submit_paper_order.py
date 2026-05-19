
"""
IBKR paper order submission test.

This script submits a tiny IBKR paper limit order only.

It is blocked unless safety settings allow paper orders.

Recommended first test:
- BUY 1 SPY
- Limit price = 1.00
This should normally not fill, but it confirms order submission path.
"""

import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent
BROKERS_PATH = PROJECT_PATH / "brokers"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(BROKERS_PATH) not in sys.path:
    sys.path.append(str(BROKERS_PATH))

from broker_factory import get_broker

from config import (
    EXECUTION_MODE,
    DEFAULT_BROKER,
    ALLOW_LIVE_TRADING,
    IBKR_TRADING_MODE,
    IBKR_READ_ONLY,
    IBKR_ENABLE_ORDERS
)


def main():
    print("IBKR Paper Order Submission Test")
    print("================================")
    print("Execution Mode:", EXECUTION_MODE)
    print("Default Broker:", DEFAULT_BROKER)
    print("Allow Live Trading:", ALLOW_LIVE_TRADING)
    print("IBKR Trading Mode:", IBKR_TRADING_MODE)
    print("IBKR Read Only:", IBKR_READ_ONLY)
    print("IBKR Enable Orders:", IBKR_ENABLE_ORDERS)

    print("\nThis script will attempt to submit a PAPER limit order only.")
    print("Test order: BUY 1 SPY LMT 1.00")
    print("No live order should be possible with current safety settings.")

    confirmation = input("\nType PAPER to continue: ").strip().upper()

    if confirmation != "PAPER":
        print("Confirmation failed. No order submitted.")
        return

    broker = get_broker("ibkr")

    try:
        result = broker.submit_order(
            ticker="SPY",
            side="BUY",
            quantity=1,
            order_type="LMT",
            limit_price=1.00
        )

        print("\nPaper order submission result:")
        print(result)

    except Exception as e:
        print("\nPaper order submission failed or was blocked.")
        print(type(e).__name__)
        print(e)

    finally:
        try:
            broker.disconnect()
            print("\nDisconnected safely.")
        except Exception:
            pass


if __name__ == "__main__":
    main()
