
"""
IBKR paper order submission test.

This script submits a tiny IBKR paper limit order only after:
- user types PAPER
- broker risk manager approves the order
- IBKR safety settings allow paper orders

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
from risk_manager import create_risk_manager_from_config

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

    ticker = "SPY"
    side = "BUY"
    quantity = 1
    order_type = "LMT"
    limit_price = 1.00
    estimated_order_value = quantity * limit_price

    print("\nThis script will attempt to submit a PAPER limit order only.")
    print(f"Test order: {side} {quantity} {ticker} {order_type} {limit_price}")
    print("No live order should be possible with current safety settings.")

    confirmation = input("\nType PAPER to continue: ").strip().upper()

    manual_confirmation_given = confirmation == "PAPER"

    if not manual_confirmation_given:
        print("Confirmation failed. No order submitted.")
        return

    risk_manager = create_risk_manager_from_config()

    risk_result = risk_manager.approve_broker_order(
        ticker=ticker,
        side=side,
        quantity=quantity,
        order_type=order_type,
        asset_type="etf",
        proposed_position_size=0.01,
        estimated_price=limit_price,
        estimated_order_value=estimated_order_value,
        current_position_quantity=0,
        manual_confirmation_given=manual_confirmation_given,
        broker_name="ibkr",
        execution_mode=EXECUTION_MODE,
        live_order=False
    )

    print("\nRisk Check Result")
    print("-----------------")
    print("Approved:", risk_result.approved)
    print("Reason:", risk_result.reason)

    if not risk_result.approved:
        print("Order blocked by risk manager. No order submitted.")
        return

    broker = get_broker("ibkr")

    try:
        result = broker.submit_order(
            ticker=ticker,
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price
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
