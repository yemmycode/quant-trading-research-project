
"""
IBKR market data test.

This script connects to IBKR TWS / IB Gateway and requests market data
for a US stock/ETF contract.

It does not place orders.
It does not modify the account.
"""

from ib_insync import IB, Stock

from config import (
    IBKR_HOST,
    IBKR_PORT,
    IBKR_CLIENT_ID,
    IBKR_TRADING_MODE,
    IBKR_READ_ONLY,
    validate_ibkr_settings
)


def get_price_from_ticker(ticker_data):
    """
    Extract a useful price from an ib_insync ticker object.

    Preference order:
    1. marketPrice()
    2. last
    3. close
    4. bid/ask midpoint
    """

    market_price = ticker_data.marketPrice()

    if market_price is not None and market_price == market_price and market_price > 0:
        return market_price, "marketPrice"

    if ticker_data.last is not None and ticker_data.last == ticker_data.last and ticker_data.last > 0:
        return ticker_data.last, "last"

    if ticker_data.close is not None and ticker_data.close == ticker_data.close and ticker_data.close > 0:
        return ticker_data.close, "close"

    if (
        ticker_data.bid is not None
        and ticker_data.ask is not None
        and ticker_data.bid == ticker_data.bid
        and ticker_data.ask == ticker_data.ask
        and ticker_data.bid > 0
        and ticker_data.ask > 0
    ):
        return (ticker_data.bid + ticker_data.ask) / 2, "bid_ask_midpoint"

    return None, "unavailable"


def main():
    print("IBKR Market Data Test")
    print("=====================")
    print("Host:", IBKR_HOST)
    print("Port:", IBKR_PORT)
    print("Client ID:", IBKR_CLIENT_ID)
    print("Trading Mode:", IBKR_TRADING_MODE)
    print("Read Only:", IBKR_READ_ONLY)

    symbol = "SPY"

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

        print("\nRequesting delayed market data mode...")
        ib.reqMarketDataType(3)

        contract = Stock(symbol, "SMART", "USD")

        print("Qualifying contract:", contract)
        qualified_contracts = ib.qualifyContracts(contract)

        if not qualified_contracts:
            print("Contract could not be qualified.")
            return

        contract = qualified_contracts[0]
        print("Qualified contract:", contract)

        print(f"\nRequesting market data for {symbol}...")
        ticker_data = ib.reqMktData(contract, "", False, False)

        ib.sleep(5)

        price, price_source = get_price_from_ticker(ticker_data)

        print("\nMarket Data Result")
        print("------------------")
        print("Symbol:", symbol)
        print("Bid:", ticker_data.bid)
        print("Ask:", ticker_data.ask)
        print("Last:", ticker_data.last)
        print("Close:", ticker_data.close)
        print("Market Price:", ticker_data.marketPrice())
        print("Selected Price:", price)
        print("Price Source:", price_source)

        ib.cancelMktData(contract)

        print("\nMarket data test completed successfully.")
        print("No orders were placed.")

    except Exception as e:
        print("\nMarket data test failed.")
        print(type(e).__name__)
        print(e)

        print("\nChecklist:")
        print("1. Is TWS or IB Gateway open?")
        print("2. Are you logged into paper trading?")
        print("3. Is API socket access enabled?")
        print("4. Is the port correct?")
        print("5. Does the symbol exist?")
        print("6. Do you have real-time market data subscription, or are you using delayed mode?")
        print("7. Did account info and positions tests work first?")

    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected safely.")


if __name__ == "__main__":
    main()
