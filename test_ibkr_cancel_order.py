
"""
IBKR paper order cancellation test.

This script connects to IBKR paper mode, lists open orders,
and allows you to cancel one selected open paper order.

It does not place orders.
It does not trade live.
"""

import sys
from pathlib import Path
import pandas as pd

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
    print("IBKR Paper Order Cancellation Test")
    print("==================================")
    print("Execution Mode:", EXECUTION_MODE)
    print("Default Broker:", DEFAULT_BROKER)
    print("Allow Live Trading:", ALLOW_LIVE_TRADING)
    print("IBKR Trading Mode:", IBKR_TRADING_MODE)
    print("IBKR Read Only:", IBKR_READ_ONLY)
    print("IBKR Enable Orders:", IBKR_ENABLE_ORDERS)

    print("\nThis script can cancel an OPEN IBKR PAPER order only.")
    print("It cannot cancel live orders with the current safety settings.")

    broker = get_broker("ibkr")

    try:
        print("\nConnecting to IBKR Paper...")
        connected = broker.connect()
        print("Connected:", connected)

        print("\nReading open orders...")
        open_orders = broker.get_open_orders()

        if not open_orders:
            print("No open IBKR paper orders found.")
            print("Nothing to cancel.")
            return

        open_orders_df = pd.DataFrame(open_orders)
        print("\nOpen Orders:")
        print(open_orders_df.to_string(index=False))

        order_id_input = input("\nEnter the order_id to cancel: ").strip()

        if not order_id_input:
            print("No order ID entered. Cancellation stopped.")
            return

        confirmation = input(
            f"Type CANCEL to cancel paper order {order_id_input}: "
        ).strip().upper()

        if confirmation != "CANCEL":
            print("Confirmation failed. No order cancelled.")
            return

        result = broker.cancel_order(order_id_input)

        print("\nCancel Result:")
        print(result)

        print("\nReading open orders after cancellation request...")
        updated_open_orders = broker.get_open_orders()

        if not updated_open_orders:
            print("No open orders found after cancellation request.")
        else:
            updated_df = pd.DataFrame(updated_open_orders)
            print(updated_df.to_string(index=False))

    except Exception as e:
        print("\nCancellation test failed or was blocked.")
        print(type(e).__name__)
        print(e)

        print("\nChecklist:")
        print("1. Is TWS or IB Gateway open?")
        print("2. Are you logged into IBKR paper trading?")
        print("3. Is API socket access enabled?")
        print("4. Is Read-Only API unchecked for paper order cancellation?")
        print("5. Is IBKR_READ_ONLY=false in .env?")
        print("6. Is IBKR_ENABLE_ORDERS=true in .env?")
        print("7. Is there actually an open paper order to cancel?")

    finally:
        try:
            broker.disconnect()
            print("\nDisconnected safely.")
        except Exception:
            pass


if __name__ == "__main__":
    main()
