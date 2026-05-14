
import sys
from pathlib import Path
from datetime import datetime
import argparse

import pandas as pd


# ==============================
# Project Paths
# ==============================

PROJECT_PATH = Path(r"C:\Users\yemi\OneDrive\Desktop\quant_trading_project")
STRATEGIES_PATH = PROJECT_PATH / "strategies"
DEFAULT_RESULTS_PATH = PROJECT_PATH / "results"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(STRATEGIES_PATH) not in sys.path:
    sys.path.append(str(STRATEGIES_PATH))


from moving_average_strategy import run_backtest
from rsi_strategy import run_rsi_backtest

from risk_manager import create_risk_manager_from_config

from config import (
    START_DATE,
    END_DATE,
    INITIAL_CAPITAL,
    POSITION_SIZE,
    TRADING_COST,
    REGIME_WINDOW
)


def get_latest_recommendation(position, signal):
    """
    Convert latest position and signal into a simple paper trading recommendation.
    """

    if position == 1:
        return "HOLD / PAPER LONG"
    elif signal == 1:
        return "BUY SIGNAL / ENTER PAPER POSITION"
    else:
        return "STAY IN CASH / NO POSITION"


def run_paper_trading_check(
    strategy_type="moving_average",
    ticker="SPY",
    results_path=None,
    short_window=20,
    long_window=50,
    rsi_window=14,
    oversold_level=30,
    overbought_level=70,
    start_date=START_DATE,
    end_date=END_DATE,
    initial_capital=INITIAL_CAPITAL,
    position_size=POSITION_SIZE,
    trading_cost=TRADING_COST,
    regime_window=REGIME_WINDOW
):
    """
    Run a paper trading status check for one strategy and one ticker.
    This does not place real trades.
    """

    if results_path is None:
        results_path = DEFAULT_RESULTS_PATH
    else:
        results_path = Path(results_path)

    results_path.mkdir(parents=True, exist_ok=True)

    if strategy_type == "moving_average":
        data, summary, trade_log = run_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            short_window=short_window,
            long_window=long_window,
            regime_window=regime_window,
            position_size=position_size,
            trading_cost=trading_cost,
            initial_capital=initial_capital
        )

        strategy_label = f"Moving Average {short_window}/{long_window}"

    elif strategy_type == "rsi":
        data, summary, trade_log = run_rsi_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            rsi_window=rsi_window,
            oversold_level=oversold_level,
            overbought_level=overbought_level,
            regime_window=regime_window,
            position_size=position_size,
            trading_cost=trading_cost,
            initial_capital=initial_capital
        )

        strategy_label = f"RSI {rsi_window} {oversold_level}/{overbought_level}"

    else:
        raise ValueError("strategy_type must be either 'moving_average' or 'rsi'.")

    latest_row = data.iloc[-1]

    latest_date = data.index[-1]
    latest_close = latest_row["Close"]
    latest_signal = int(latest_row["Signal"])
    latest_position = int(latest_row["Position"])
    latest_strategy_growth = latest_row["Strategy_Growth"]
    latest_paper_value = initial_capital * latest_strategy_growth

    recommendation = get_latest_recommendation(
        position=latest_position,
        signal=latest_signal
    )

    risk_manager = create_risk_manager_from_config()

    risk_check = risk_manager.approve_order(
        ticker=ticker,
        proposed_position_size=position_size,
        current_daily_loss=0.00,
        current_weekly_loss=0.00,
        current_total_drawdown=0.00,
        manual_confirmation_given=True,
        live_order=False
    )

    if not risk_check.approved:
        recommendation = f"BLOCKED BY RISK MANAGER: {risk_check.reason}"

    status = pd.DataFrame([
        {
            "Generated At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ticker": ticker,
            "Strategy Type": strategy_type,
            "Strategy Label": strategy_label,
            "Latest Data Date": latest_date,
            "Latest Close": latest_close,
            "Latest Signal": latest_signal,
            "Latest Position": latest_position,
            "Recommendation": recommendation,
            "Initial Capital": initial_capital,
            "Position Size": position_size,
            "Trading Cost": trading_cost,
            "Paper Portfolio Value": latest_paper_value
        }
    ])

    output_file = results_path / f"paper_trading_status_{ticker}_{strategy_type}.csv"
    status.to_csv(output_file, index=False)

    print("\nPaper trading check completed.")
    print(status.to_string(index=False))
    print(f"\nStatus saved to: {output_file}")

    return status, data, summary, trade_log


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run paper trading status check.")

    parser.add_argument(
        "--strategy",
        type=str,
        default="moving_average",
        choices=["moving_average", "rsi"],
        help="Strategy type to run."
    )

    parser.add_argument(
        "--ticker",
        type=str,
        default="SPY",
        help="Ticker to check."
    )

    parser.add_argument(
        "--results-path",
        type=str,
        default=None,
        help="Optional folder where paper trading status should be saved."
    )

    args = parser.parse_args()

    run_paper_trading_check(
        strategy_type=args.strategy,
        ticker=args.ticker,
        results_path=args.results_path
    )
