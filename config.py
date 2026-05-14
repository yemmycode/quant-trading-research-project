
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
