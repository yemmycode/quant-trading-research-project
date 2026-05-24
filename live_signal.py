
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
    short_window=20,
    long_window=50,
    start_date=None,
    end_date=None,
    initial_capital=10000,
    exit_window=30,
    **kwargs
):
    """
    Generate the latest signal safely.

    This version prevents the dashboard from crashing when market data is unavailable.
    It returns a non-actionable NO DATA signal instead of raising an exception.

    Returns:
        signal_result, signal_data, signal_summary, signal_trade_log
    """

    import inspect
    from datetime import datetime

    ticker = str(ticker or "SPY").strip().upper()

    try:
        # Build candidate parameters for run_backtest.
        candidate_params = {
            "ticker": ticker,
            "short_window": int(short_window),
            "long_window": int(long_window),
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": float(initial_capital),
            "exit_window": int(exit_window),
        }

        # Include any extra parameters passed by the dashboard.
        candidate_params.update(kwargs)

        # Only pass parameters accepted by run_backtest.
        run_backtest_signature = inspect.signature(run_backtest)
        accepted_params = {}

        for key, value in candidate_params.items():
            if key in run_backtest_signature.parameters and value is not None:
                accepted_params[key] = value

        data, summary, trade_log = run_backtest(**accepted_params)

    except Exception as data_error:
        error_message = str(data_error)

        signal_result = {
            "ticker": ticker,
            "action": "NO DATA",
            "signal_action": "NO DATA",
            "reason": f"Could not generate signal because market data was unavailable: {error_message}",
            "latest_close": None,
            "latest_date": None,
            "strategy_label": strategy_name,
            "strategy_name": strategy_name,
            "data_error": error_message,
            "actionable": False,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        signal_summary = {
            "status": "failed",
            "reason": "market_data_unavailable",
            "error": error_message,
            "ticker": ticker,
        }

        return signal_result, None, signal_summary, None

    try:
        if data is None or getattr(data, "empty", False):
            signal_result = {
                "ticker": ticker,
                "action": "NO DATA",
                "signal_action": "NO DATA",
                "reason": "No market data was returned for this ticker.",
                "latest_close": None,
                "latest_date": None,
                "strategy_label": strategy_name,
                "strategy_name": strategy_name,
                "data_error": "empty_data",
                "actionable": False,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            signal_summary = {
                "status": "failed",
                "reason": "empty_market_data",
                "ticker": ticker,
            }

            return signal_result, data, signal_summary, trade_log

        # Extract latest close safely.
        latest_close = None
        latest_date = None

        try:
            latest_date = str(data.index[-1])
        except Exception:
            latest_date = None

        try:
            if "Close" in data.columns:
                latest_close = float(data["Close"].dropna().iloc[-1])
            elif "close" in data.columns:
                latest_close = float(data["close"].dropna().iloc[-1])
            else:
                # Handles possible MultiIndex columns from yfinance.
                close_columns = [
                    col for col in data.columns
                    if isinstance(col, tuple) and "Close" in col
                ]

                if close_columns:
                    latest_close = float(data[close_columns[0]].dropna().iloc[-1])
        except Exception:
            latest_close = None

        # Try to infer action from the latest row.
        action = "HOLD"
        reason = "Signal generated successfully."

        try:
            latest_row = data.iloc[-1]

            for possible_col in ["Signal", "signal", "Action", "action", "Position", "position"]:
                if possible_col in data.columns:
                    value = latest_row[possible_col]

                    if value == 1 or str(value).upper() == "BUY":
                        action = "BUY"
                        reason = "Latest strategy signal indicates BUY."
                    elif value == -1 or str(value).upper() == "SELL":
                        action = "SELL"
                        reason = "Latest strategy signal indicates SELL."
                    else:
                        action = "HOLD"
                        reason = "Latest strategy signal indicates HOLD."

                    break

        except Exception:
            action = "HOLD"
            reason = "Signal generated, but latest action column could not be inferred. Defaulting to HOLD."

        signal_result = {
            "ticker": ticker,
            "action": action,
            "signal_action": action,
            "reason": reason,
            "latest_close": latest_close,
            "latest_date": latest_date,
            "strategy_label": strategy_name,
            "strategy_name": strategy_name,
            "actionable": action in ["BUY", "SELL"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        signal_summary = summary

        if signal_summary is None:
            signal_summary = {}

        if isinstance(signal_summary, dict):
            signal_summary["latest_signal_action"] = action
            signal_summary["latest_signal_ticker"] = ticker
            signal_summary["latest_signal_generated_at"] = signal_result["generated_at"]

        return signal_result, data, signal_summary, trade_log

    except Exception as signal_error:
        error_message = str(signal_error)

        signal_result = {
            "ticker": ticker,
            "action": "ERROR",
            "signal_action": "ERROR",
            "reason": f"Signal generation failed after data download: {error_message}",
            "latest_close": None,
            "latest_date": None,
            "strategy_label": strategy_name,
            "strategy_name": strategy_name,
            "data_error": error_message,
            "actionable": False,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        signal_summary = {
            "status": "failed",
            "reason": "signal_processing_error",
            "error": error_message,
            "ticker": ticker,
        }

        return signal_result, data, signal_summary, trade_log
