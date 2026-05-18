
"""
IBKR configuration test.

This script validates local IBKR config values.
It does not connect to IBKR.
It does not place trades.
"""

from config import (
    IBKR_HOST,
    IBKR_PORT,
    IBKR_CLIENT_ID,
    IBKR_ACCOUNT_ID,
    IBKR_TRADING_MODE,
    IBKR_READ_ONLY,
    IBKR_ENABLE_ORDERS,
    validate_ibkr_settings
)


def main():
    print("IBKR Config Test")
    print("================")
    print("Host:", IBKR_HOST)
    print("Port:", IBKR_PORT)
    print("Client ID:", IBKR_CLIENT_ID)
    print("Account ID:", IBKR_ACCOUNT_ID if IBKR_ACCOUNT_ID else "[not set]")
    print("Trading Mode:", IBKR_TRADING_MODE)
    print("Read Only:", IBKR_READ_ONLY)
    print("Enable Orders:", IBKR_ENABLE_ORDERS)

    print("\nValidation:", validate_ibkr_settings())
    print("\nNo broker connection was attempted.")


if __name__ == "__main__":
    main()
