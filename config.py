import os
from dotenv import load_dotenv

load_dotenv()

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

# ==============================
# Dashboard Authentication
# ==============================




# ==============================
# Dashboard Authentication
# ==============================

DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "demo-password")


# ==============================
# Live Trading Safety Settings
# ==============================

# Live trading must remain disabled by default.
LIVE_TRADING_ENABLED = False

# Manual confirmation should remain required before any real order.
REQUIRE_MANUAL_CONFIRMATION = True

# Maximum fraction of account allowed in one position.
# 0.10 = 10%
MAX_POSITION_SIZE = 0.10

# Maximum daily loss allowed before blocking trading.
# 0.02 = 2%
MAX_DAILY_LOSS = 0.02

# Maximum weekly loss allowed before blocking trading.
# 0.05 = 5%
MAX_WEEKLY_LOSS = 0.05

# Maximum total drawdown allowed before blocking trading.
# 0.10 = 10%
MAX_TOTAL_DRAWDOWN = 0.10

# Only these tickers are allowed for future live/paper order checks.
ALLOWED_TICKERS = ["SPY", "QQQ"]

# Emergency stop blocks all future trading checks.
EMERGENCY_STOP = False