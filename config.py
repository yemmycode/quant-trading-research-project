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
    "rsi",
    "bollinger_bands",
    "momentum",
    "breakout"
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
ALLOWED_TICKERS = [
    "SPY",
    "QQQ"
]

# Emergency stop blocks all future trading checks.
EMERGENCY_STOP = False


# ==============================
# Dashboard Authentication
# ==============================

# Simple demo password for Streamlit dashboard access.
# For production, use environment variables or a proper authentication system.
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "demo-password")

# Bollinger Bands parameter combinations
BOLLINGER_PARAMETER_SETS = [
    {"window": 20, "num_std": 2},
    {"window": 20, "num_std": 2.5},
    {"window": 30, "num_std": 2},
]

# Momentum parameter combinations
MOMENTUM_PARAMETER_SETS = [
    {"momentum_window": 30},
    {"momentum_window": 60},
    {"momentum_window": 90},
]

# Breakout parameter combinations
BREAKOUT_PARAMETER_SETS = [
    {"breakout_window": 50, "exit_window": 20},
    {"breakout_window": 100, "exit_window": 30},
    {"breakout_window": 120, "exit_window": 50},
]
