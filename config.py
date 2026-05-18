
# ==============================
# Quant Trading Project Settings
# ==============================

# Test period
START_DATE = "2018-01-01"
END_DATE = "2025-01-01"

# Starting capital
INITIAL_CAPITAL = 10000

# Strategy exposure
POSITION_SIZE = 0.50

# Estimated trading cost per transaction
# 0.001 = 0.10%
TRADING_COST = 0.001

# Market regime filter
REGIME_WINDOW = 200

# Strategies to run
STRATEGIES = [
    "moving_average",
    "rsi"
]

# Assets to test
TICKERS = [
    "SPY",
    "QQQ",
    "AAPL",
    "MSFT",
    "TSLA"
]

# Moving average parameter combinations
MOVING_AVERAGE_PARAMETER_SETS = [
    {"short_window": 10, "long_window": 50},
    {"short_window": 20, "long_window": 50},
    {"short_window": 20, "long_window": 100},
    {"short_window": 50, "long_window": 200},
]

# RSI parameter combinations
RSI_PARAMETER_SETS = [
    {"rsi_window": 14, "oversold_level": 30, "overbought_level": 70},
    {"rsi_window": 14, "oversold_level": 35, "overbought_level": 65},
    {"rsi_window": 21, "oversold_level": 30, "overbought_level": 70},
]


# ==============================
# Execution Mode Settings
# ==============================

# BACKTEST = research/backtesting only
# BROKER_PAPER = connected broker paper/sandbox trading
# LIVE_MANUAL = live broker trading with manual confirmation only

EXECUTION_MODE = "BACKTEST"

SUPPORTED_EXECUTION_MODES = [
    "BACKTEST",
    "BROKER_PAPER",
    "LIVE_MANUAL"
]

DEFAULT_BROKER = "paper"

SUPPORTED_BROKERS = [
    "paper",
    "ibkr",
    "alpaca"
]

PRIMARY_MARKET = "US"
DEFAULT_CURRENCY = "USD"
ALLOW_LIVE_TRADING = False

def validate_execution_settings():
    """Validate execution mode and broker settings."""

    if EXECUTION_MODE not in SUPPORTED_EXECUTION_MODES:
        raise ValueError(
            f"Invalid EXECUTION_MODE: {EXECUTION_MODE}. "
            f"Supported modes: {SUPPORTED_EXECUTION_MODES}"
        )

    if DEFAULT_BROKER not in SUPPORTED_BROKERS:
        raise ValueError(
            f"Invalid DEFAULT_BROKER: {DEFAULT_BROKER}. "
            f"Supported brokers: {SUPPORTED_BROKERS}"
        )

    if EXECUTION_MODE == "LIVE_MANUAL" and not ALLOW_LIVE_TRADING:
        raise ValueError(
            "LIVE_MANUAL mode is selected, but ALLOW_LIVE_TRADING is False. "
            "This is blocked for safety."
        )

    return True