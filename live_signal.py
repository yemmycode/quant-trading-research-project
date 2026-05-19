
"""
Live Broker Signal Generator

This module generates the latest trading signal from supported strategies.

It does not place orders.
It does not connect to a broker.
It only produces a decision such as:
- BUY
- SELL
- HOLD
- STAY IN CASH
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_PATH = Path(__file__).resolve().parent
STRATEGIES_PATH = PROJECT_PATH / "strategies"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(STRATEGIES_PATH) not in sys.path:
    sys.path.append(str(STRATEGIES_PATH))

from moving_average_strategy import run_backtest
from rsi_strategy import run_rsi_backtest
from bollinger_bands_strategy import run_bollinger_backtest
from momentum_strategy import run_momentum_backtest
from breakout_strategy import run_breakout_backtest


SUPPORTED_LIVE_SIGNAL_STRATEGIES = [
    "moving_average",
    "rsi",
    "bollinger_bands",
    "momentum",
    "breakout"
]


def normalize_strategy_name(strategy_name):
    """
    Normalize strategy name to internal key.
    """

    if strategy_name is None:
        raise ValueError("strategy_name cannot be None.")

    strategy_name = str(strategy_name).strip().lower().replace(" ", "_")

    aliases = {
        "moving_average": "moving_average",
        "ma": "moving_average",
        "rsi": "rsi",
        "bollinger": "bollinger_bands",
        "bollinger_bands": "bollinger_bands",
        "momentum": "momentum",
        "breakout": "breakout"
    }

    if strategy_name not in aliases:
        raise ValueError(
            f"Unsupported strategy: {strategy_name}. "
            f"Supported strategies: {SUPPORTED_LIVE_SIGNAL_STRATEGIES}"
        )

    return aliases[strategy_name]


def interpret_latest_signal(data):
    """
    Convert latest strategy data row into a simple action.

    Logic:
    - If latest signal is 1 and previous signal is 0 => BUY
    - If latest signal is 0 and previous signal is 1 => SELL
    - If latest signal is 1 and previous signal is 1 => HOLD
    - If latest signal is 0 and previous signal is 0 => STAY IN CASH
    """

    if data is None or data.empty:
        raise ValueError("Cannot interpret signal from empty data.")

    if "Signal" not in data.columns:
        raise ValueError("Data does not contain a Signal column.")

    clean_data = data.dropna(subset=["Signal"]).copy()

    if len(clean_data) < 2:
        raise ValueError("Not enough signal data to compare latest and previous signal.")

    latest_row = clean_data.iloc[-1]
    previous_row = clean_data.iloc[-2]

    latest_signal = int(latest_row["Signal"])
    previous_signal = int(previous_row["Signal"])

    latest_close = float(latest_row["Close"]) if "Close" in clean_data.columns else None
    latest_date = clean_data.index[-1]

    if latest_signal == 1 and previous_signal == 0:
        action = "BUY"
        reason = "Signal changed from 0 to 1."

    elif latest_signal == 0 and previous_signal == 1:
        action = "SELL"
        reason = "Signal changed from 1 to 0."

    elif latest_signal == 1 and previous_signal == 1:
        action = "HOLD"
        reason = "Signal remains invested."

    else:
        action = "STAY IN CASH"
        reason = "Signal remains out of market."

    return {
        "action": action,
        "reason": reason,
        "latest_signal": latest_signal,
        "previous_signal": previous_signal,
        "latest_close": latest_close,
        "latest_date": str(latest_date),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def generate_live_signal(
    ticker="SPY",
    strategy_name="moving_average",
    start_date="2018-01-01",
    end_date=None,
    initial_capital=10000,
    position_size=0.50,
    trading_cost=0.001,
    regime_window=200,
    short_window=20,
    long_window=50,
    rsi_window=14,
    oversold_level=30,
    overbought_level=70,
    bollinger_window=20,
    bollinger_std=2,
    momentum_window=60,
    breakout_window=50,
    exit_window=20
):
    """
    Generate the latest signal for a selected strategy.
    """

    strategy_key = normalize_strategy_name(strategy_name)

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    ticker = str(ticker).strip().upper()

    if strategy_key == "moving_average":
        data, summary, trade_log = run_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            short_window=int(short_window),
            long_window=int(long_window),
            regime_window=int(regime_window),
            position_size=float(position_size),
            trading_cost=float(trading_cost),
            initial_capital=float(initial_capital)
        )

        strategy_label = f"Moving Average {short_window}/{long_window}"

    elif strategy_key == "rsi":
        data, summary, trade_log = run_rsi_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            rsi_window=int(rsi_window),
            oversold_level=int(oversold_level),
            overbought_level=int(overbought_level),
            regime_window=int(regime_window),
            position_size=float(position_size),
            trading_cost=float(trading_cost),
            initial_capital=float(initial_capital)
        )

        strategy_label = f"RSI {rsi_window} {oversold_level}/{overbought_level}"

    elif strategy_key == "bollinger_bands":
        data, summary, trade_log = run_bollinger_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            window=int(bollinger_window),
            num_std=float(bollinger_std),
            regime_window=int(regime_window),
            position_size=float(position_size),
            trading_cost=float(trading_cost),
            initial_capital=float(initial_capital)
        )

        strategy_label = f"Bollinger Bands {bollinger_window}/{bollinger_std}"

    elif strategy_key == "momentum":
        data, summary, trade_log = run_momentum_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            momentum_window=int(momentum_window),
            regime_window=int(regime_window),
            position_size=float(position_size),
            trading_cost=float(trading_cost),
            initial_capital=float(initial_capital)
        )

        strategy_label = f"Momentum {momentum_window}"

    elif strategy_key == "breakout":
        data, summary, trade_log = run_breakout_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            breakout_window=int(breakout_window),
            exit_window=int(exit_window),
            regime_window=int(regime_window),
            position_size=float(position_size),
            trading_cost=float(trading_cost),
            initial_capital=float(initial_capital)
        )

        strategy_label = f"Breakout {breakout_window}/{exit_window}"

    else:
        raise ValueError(f"Unhandled strategy key: {strategy_key}")

    signal_result = interpret_latest_signal(data)

    signal_result.update({
        "ticker": ticker,
        "strategy_key": strategy_key,
        "strategy_label": strategy_label,
        "start_date": start_date,
        "end_date": end_date
    })

    return signal_result, data, summary, trade_log
