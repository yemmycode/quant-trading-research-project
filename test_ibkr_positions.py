
"""
IBKR paper positions test.

This script connects to IBKR TWS / IB Gateway and reads current paper positions.
It does not place orders.
It does not modify the account.
"""

from ib_insync import IB

from config import (
    IBKR_HOST,
    IBKR_PORT,
    IBKR_CLIENT_ID,
    IBKR_TRADING_MODE,
    IBKR_READ_ONLY,
    validate_ibkr_settings
)


def main():
    print("IBKR Paper Positions Test")
    print("=========================")
    print("Host:", IBKR_HOST)
    print("Port:", IBKR_PORT)
    print("Client ID:", IBKR_CLIENT_ID)
    print("Trading Mode:", IBKR_TRADING_MODE)
    print("Read Only:", IBKR_READ_ONLY)

    print("\nValidating IBKR settings...")
    validate_ibkr_settings()
    print("Validation passed.")

    ib = IB()

    try:
        print("\nConnecting to IBKR...")
        ib.connect(
            host=IBKR_HOST,
            port=IBKR_PORT,
            clientId=IBKR_CLIENT_ID,
            timeout=10
        )

        print("Connected:", ib.isConnected())

        accounts = ib.managedAccounts()
        print("Managed Accounts:", accounts)

        print("\nRequesting positions...")
        positions = ib.positions()

        if not positions:
            print("No open positions found in the IBKR paper account.")
            print("This is normal if you have not placed any paper trades yet.")
        else:
            print("\nOpen Paper Positions")
            print("--------------------")

            for position in positions:
                contract = position.contract

                symbol = getattr(contract, "symbol", "")
                sec_type = getattr(contract, "secType", "")
                exchange = getattr(contract, "exchange", "")
                currency = getattr(contract, "currency", "")

                print("Account:", position.account)
                print("Symbol:", symbol)
                print("Security Type:", sec_type)
                print("Exchange:", exchange)
                print("Currency:", currency)
                print("Quantity:", position.position)
                print("Average Cost:", position.avgCost)
                print("-" * 40)

        print("\nPositions test completed successfully.")
        print("No orders were placed.")

    except Exception as e:
        print("\nPositions test failed.")
        print(type(e).__name__)
        print(e)

        print("\nChecklist:")
        print("1. Is TWS or IB Gateway open?")
        print("2. Are you logged into paper trading?")
        print("3. Is API socket access enabled?")
        print("4. Is the port correct?")
        print("5. Is the client ID available?")
        print("6. Did the account info test work first?")

    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected safely.")


if __name__ == "__main__":
    main()
