
"""
IBKR Contract Builder

This module creates IBKR contract objects for supported instruments.

Initial supported scope:
- US stocks
- US ETFs
- USD currency
- SMART exchange routing

No options.
No futures.
No forex.
No crypto.
No leveraged/complex instruments unless explicitly allowed later.
"""

from ib_insync import Stock


DEFAULT_EXCHANGE = "SMART"
DEFAULT_CURRENCY = "USD"


SUPPORTED_SECURITY_TYPES = [
    "STK"
]


DEFAULT_ALLOWED_SYMBOLS = [
    "SPY",
    "QQQ",
    "AAPL",
    "MSFT"
]


def normalize_symbol(symbol):
    """
    Normalize ticker symbol input.
    """

    if symbol is None:
        raise ValueError("Symbol cannot be None.")

    symbol = str(symbol).strip().upper()

    if not symbol:
        raise ValueError("Symbol cannot be empty.")

    return symbol


def validate_us_stock_symbol(symbol, allowed_symbols=None):
    """
    Validate that the symbol is allowed for early-stage IBKR testing.
    """

    symbol = normalize_symbol(symbol)

    if allowed_symbols is None:
        allowed_symbols = DEFAULT_ALLOWED_SYMBOLS

    allowed_symbols = [str(item).upper() for item in allowed_symbols]

    if symbol not in allowed_symbols:
        raise ValueError(
            f"Symbol '{symbol}' is not currently allowed for IBKR testing. "
            f"Allowed symbols: {allowed_symbols}"
        )

    return symbol


def build_us_stock_contract(
    symbol,
    exchange=DEFAULT_EXCHANGE,
    currency=DEFAULT_CURRENCY,
    allowed_symbols=None
):
    """
    Build an IBKR Stock contract for US stocks/ETFs.

    Example:
        build_us_stock_contract("SPY")
    """

    symbol = validate_us_stock_symbol(
        symbol=symbol,
        allowed_symbols=allowed_symbols
    )

    contract = Stock(
        symbol,
        exchange,
        currency
    )

    return contract


def describe_contract(contract):
    """
    Return a simple dictionary description of a contract.
    """

    return {
        "symbol": getattr(contract, "symbol", None),
        "secType": getattr(contract, "secType", None),
        "exchange": getattr(contract, "exchange", None),
        "currency": getattr(contract, "currency", None)
    }


def build_contract_from_order_request(order_request):
    """
    Build a contract from an order request dictionary.

    Expected order_request example:
        {
            "ticker": "SPY",
            "asset_type": "stock",
            "exchange": "SMART",
            "currency": "USD"
        }
    """

    ticker = order_request.get("ticker")
    asset_type = order_request.get("asset_type", "stock").lower()
    exchange = order_request.get("exchange", DEFAULT_EXCHANGE)
    currency = order_request.get("currency", DEFAULT_CURRENCY)

    if asset_type not in ["stock", "etf"]:
        raise ValueError(
            f"Unsupported asset_type: {asset_type}. "
            "Only stock and ETF are supported for now."
        )

    return build_us_stock_contract(
        symbol=ticker,
        exchange=exchange,
        currency=currency
    )
