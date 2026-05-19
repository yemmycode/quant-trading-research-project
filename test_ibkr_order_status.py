
"""
IBKR paper order status test.

This script connects to IBKR paper mode and reads open orders / order statuses.
It does not place orders.
It does not cancel orders.
It does not modify the account.
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
    print("IBKR Paper Order Status Test")
    print("============================")
    print("Execution Mode:", EXECUTION_MODE)
    print("Default Broker:", DEFAULT_BROKER)
    print("Allow Live Trading:", ALLOW_LIVE_TRADING)
    print("IBKR Trading Mode:", IBKR_TRADING_MODE)
    print("IBKR Read Only:", IBKR_READ_ONLY)
    print("IBKR Enable Orders:", IBKR_ENABLE_ORDERS)

    broker = get_broker("ibkr")

    try:
        print("\\nConnecting to IBKR Paper...")
        connected = broker.connect()
        print("Connected:", connected)

        print("\\nReading open orders...")
        open_orders = broker.get_open_orders()

        if not open_orders:
            print("No open IBKR paper orders found.")
            print("If you submitted the SPY LMT 1.00 order earlier and cancelled it, this is normal.")
        else:
            open_orders_df = pd.DataFrame(open_orders)
            print("\\nOpen Orders:")
            print(open_orders_df.to_string(index=False))

        print("\\nReading all trades known to this API session...")
        all_trades = broker.get_all_trades()

        if not all_trades:
            print("No trades found in the current IBKR API session.")
        else:
            trades_df = pd.DataFrame(all_trades)
            print("\\nTrades:")
            print(trades_df.to_string(index=False))

        if open_orders:
            first_order_id = open_orders[0]["order_id"]
            print(f"\\nChecking first open order status: {first_order_id}")

            status = broker.get_order_status(first_order_id)
            print(status)
        else:
            print("\\nNo open order ID available for specific status lookup.")

        print("\\nOrder status test completed.")
        print("No orders were placed.")
        print("No orders were cancelled.")

    except Exception as e:
        print("\\nOrder status test failed.")
        print(type(e).__name__)
        print(e)

        print("\\nChecklist:")
        print("1. Is TWS or IB Gateway open?")
        print("2. Are you logged into IBKR paper trading?")
        print("3. Is API socket access enabled?")
        print("4. Is the port correct?")
        print("5. Did Lesson 66 connection test work?")
        print("6. Did Lesson 72 paper order test create an order?")

    finally:
        try:
            broker.disconnect()
            print("\\nDisconnected safely.")
        except Exception:
            pass


if __name__ == "__main__":
    main()
