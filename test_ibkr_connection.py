
"""
IBKR paper connection test.

This script connects to IBKR TWS / IB Gateway in read-only mode.
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
    print("IBKR Paper Connection Test")
    print("==========================")
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
        print("\nAttempting connection to IBKR...")
        ib.connect(
            host=IBKR_HOST,
            port=IBKR_PORT,
            clientId=IBKR_CLIENT_ID,
            timeout=10
        )

        print("Connected:", ib.isConnected())

        managed_accounts = ib.managedAccounts()
        print("Managed Accounts:", managed_accounts)

        print("\nConnection test completed successfully.")
        print("No orders were placed.")

    except Exception as e:
        print("\nConnection test failed.")
        print(type(e).__name__)
        print(e)

        print("\nChecklist:")
        print("1. Is TWS or IB Gateway open?")
        print("2. Are you logged into the paper trading environment?")
        print("3. Is API socket access enabled?")
        print("4. Is the socket port correct?")
        print("5. Does IBKR_PORT in .env match TWS/Gateway?")
        print("6. Is another client already using the same client ID?")

    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected safely.")


if __name__ == "__main__":
    main()
