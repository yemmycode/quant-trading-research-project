
"""
IBKR paper account info test.

This script connects to IBKR TWS / IB Gateway and reads account summary values.
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


IMPORTANT_TAGS = [
    "NetLiquidation",
    "TotalCashValue",
    "AvailableFunds",
    "BuyingPower",
    "ExcessLiquidity",
    "EquityWithLoanValue",
    "GrossPositionValue",
    "MaintMarginReq",
    "InitMarginReq"
]


def main():
    print("IBKR Paper Account Info Test")
    print("============================")
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

        if not accounts:
            print("No managed accounts returned.")
            return

        account_id = accounts[0]
        print("Using Account:", account_id)

        print("\nRequesting account summary...")
        account_summary = ib.accountSummary(account=account_id)

        filtered_rows = []

        for item in account_summary:
            if item.tag in IMPORTANT_TAGS:
                filtered_rows.append({
                    "Account": item.account,
                    "Tag": item.tag,
                    "Value": item.value,
                    "Currency": item.currency
                })

        if not filtered_rows:
            print("No important account summary values found.")
        else:
            print("\nImportant Account Summary")
            print("-------------------------")

            for row in filtered_rows:
                print(
                    f"{row['Tag']}: {row['Value']} {row['Currency']}"
                )

        print("\nAccount info test completed successfully.")
        print("No orders were placed.")

    except Exception as e:
        print("\nAccount info test failed.")
        print(type(e).__name__)
        print(e)

        print("\nChecklist:")
        print("1. Is TWS or IB Gateway open?")
        print("2. Are you logged into paper trading?")
        print("3. Is API socket access enabled?")
        print("4. Is the port correct?")
        print("5. Is the client ID available?")
        print("6. Is your account fully active for paper trading?")

    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected safely.")


if __name__ == "__main__":
    main()
