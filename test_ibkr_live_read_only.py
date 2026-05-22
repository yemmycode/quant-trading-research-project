
"""
IBKR Live Read-Only Connection Test

This script connects to IBKR live mode in READ-ONLY mode only.

It does not place orders.
It does not cancel orders.
It does not enable live trading.
It only reads account information and positions.

Required safety settings:
- IBKR_TRADING_MODE=live
- IBKR_READ_ONLY=true
- IBKR_ENABLE_ORDERS=false
- ALLOW_LIVE_TRADING=False
- LIVE_TRADING_ENABLED=False
"""

import sys
import asyncio
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent
BROKERS_PATH = PROJECT_PATH / "brokers"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(BROKERS_PATH) not in sys.path:
    sys.path.append(str(BROKERS_PATH))


try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


from ib_insync import IB

from config import (
    IBKR_HOST,
    IBKR_PORT,
    IBKR_CLIENT_ID,
    IBKR_TRADING_MODE,
    IBKR_READ_ONLY,
    IBKR_ENABLE_ORDERS,
    ALLOW_LIVE_TRADING,
    LIVE_TRADING_ENABLED
)


def validate_live_read_only_settings():
    """
    Hard safety validation for live read-only test.
    """

    if IBKR_TRADING_MODE != "live":
        raise PermissionError(
            f"IBKR_TRADING_MODE must be 'live' for this test. Current: {IBKR_TRADING_MODE}"
        )

    if IBKR_READ_ONLY is not True:
        raise PermissionError(
            "IBKR_READ_ONLY must be True for live read-only test."
        )

    if IBKR_ENABLE_ORDERS is not False:
        raise PermissionError(
            "IBKR_ENABLE_ORDERS must be False for live read-only test."
        )

    if ALLOW_LIVE_TRADING is not False:
        raise PermissionError(
            "ALLOW_LIVE_TRADING must remain False for this read-only test."
        )

    if LIVE_TRADING_ENABLED is not False:
        raise PermissionError(
            "LIVE_TRADING_ENABLED must remain False for this read-only test."
        )


def print_account_summary(summary):
    important_tags = [
        "NetLiquidation",
        "TotalCashValue",
        "AvailableFunds",
        "BuyingPower",
        "ExcessLiquidity",
        "GrossPositionValue",
        "MaintMarginReq",
        "InitMarginReq"
    ]

    print("\nImportant Account Summary")
    print("-------------------------")

    found = False

    for item in summary:
        if item.tag in important_tags:
            found = True
            print(f"{item.tag}: {item.value} {item.currency}")

    if not found:
        print("No important account summary fields found.")


def print_positions(positions):
    print("\nLive Account Positions")
    print("----------------------")

    if not positions:
        print("No open live positions found.")
        return

    for position in positions:
        contract = position.contract

        print("Account:", position.account)
        print("Symbol:", getattr(contract, "symbol", ""))
        print("Security Type:", getattr(contract, "secType", ""))
        print("Exchange:", getattr(contract, "exchange", ""))
        print("Currency:", getattr(contract, "currency", ""))
        print("Quantity:", position.position)
        print("Average Cost:", position.avgCost)
        print("-" * 40)


def main():
    print("IBKR Live Read-Only Connection Test")
    print("===================================")
    print("Host:", IBKR_HOST)
    print("Port:", IBKR_PORT)
    print("Client ID:", IBKR_CLIENT_ID)
    print("Trading Mode:", IBKR_TRADING_MODE)
    print("Read Only:", IBKR_READ_ONLY)
    print("Enable Orders:", IBKR_ENABLE_ORDERS)
    print("Allow Live Trading:", ALLOW_LIVE_TRADING)
    print("Live Trading Enabled:", LIVE_TRADING_ENABLED)

    print("\nValidating live read-only safety settings...")
    validate_live_read_only_settings()
    print("Safety validation passed.")

    confirmation = input(
        "\nType READONLY to connect to IBKR LIVE in read-only mode: "
    ).strip().upper()

    if confirmation != "READONLY":
        print("Confirmation failed. No connection attempted.")
        return

    ib = IB()

    try:
        print("\nConnecting to IBKR LIVE read-only...")
        ib.connect(
            host=IBKR_HOST,
            port=IBKR_PORT,
            clientId=IBKR_CLIENT_ID,
            timeout=10
        )

        print("Connected:", ib.isConnected())

        accounts = ib.managedAccounts()
        print("Managed Accounts:", accounts)

        if not accounts:
            print("No managed accounts returned.")
            return

        account_id = accounts[0]
        print("Using Account:", account_id)

        summary = ib.accountSummary(account=account_id)
        print_account_summary(summary)

        positions = ib.positions()
        print_positions(positions)

        print("\nLive read-only test completed successfully.")
        print("No orders were placed.")
        print("No orders were cancelled.")
        print("No live trading was enabled.")

    except Exception as e:
        print("\nLive read-only connection failed or was blocked.")
        print(type(e).__name__)
        print(e)

        print("\nChecklist:")
        print("1. Are you logged into TWS LIVE, not paper?")
        print("2. Is TWS live API enabled?")
        print("3. Is TWS live socket port 7496?")
        print("4. Is Read-Only API checked in TWS?")
        print("5. Does .env have IBKR_PORT=7496?")
        print("6. Does .env have IBKR_READ_ONLY=true?")
        print("7. Does .env have IBKR_ENABLE_ORDERS=false?")
        print("8. Is no other API client using the same client ID?")

    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected safely.")


if __name__ == "__main__":
    main()
