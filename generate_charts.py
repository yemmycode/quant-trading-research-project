
import sys
from pathlib import Path
import argparse

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_PATH = Path(__file__).resolve().parent
STRATEGIES_PATH = PROJECT_PATH / "strategies"
DEFAULT_RESULTS_PATH = PROJECT_PATH / "results"
DEFAULT_CHARTS_PATH = PROJECT_PATH / "charts"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(STRATEGIES_PATH) not in sys.path:
    sys.path.append(str(STRATEGIES_PATH))

from moving_average_strategy import run_backtest
from rsi_strategy import run_rsi_backtest
from bollinger_bands_strategy import run_bollinger_backtest
from momentum_strategy import run_momentum_backtest
from breakout_strategy import run_breakout_backtest

from config import (
    START_DATE,
    END_DATE,
    INITIAL_CAPITAL,
    POSITION_SIZE,
    TRADING_COST,
    REGIME_WINDOW
)


def load_batch_results(results_path):
    batch_results_file = results_path / "batch_test_results.csv"

    if not batch_results_file.exists():
        raise FileNotFoundError(
            f"Could not find {batch_results_file}. Run run_batch_tests.py first."
        )

    return pd.read_csv(batch_results_file)


def get_top_strategies(batch_results, metric="Sharpe Ratio", top_n=3):
    if metric not in batch_results.columns:
        raise ValueError(f"Metric '{metric}' not found in batch results.")

    return batch_results.sort_values(by=metric, ascending=False).head(top_n)


def get_value(row, column_name, default=None):
    if column_name in row and not pd.isna(row[column_name]):
        return row[column_name]
    return default


def rerun_strategy(row):
    ticker = row["Ticker"]
    strategy_type = row.get("Strategy Type", None)

    if pd.isna(strategy_type) or strategy_type is None:
        strategy_name = row.get("Strategy", "")

        strategy_type_map = {
            "Quant Strategy": "moving_average",
            "RSI Strategy": "rsi",
            "Bollinger Bands Strategy": "bollinger_bands",
            "Momentum Strategy": "momentum",
            "Breakout Strategy": "breakout"
        }

        strategy_type = strategy_type_map.get(strategy_name, "moving_average")


    if strategy_type == "moving_average":
        short_window = int(get_value(row, "Short Window", 20))
        long_window = int(get_value(row, "Long Window", 50))

        data_result, _, _ = run_backtest(
            ticker=ticker,
            start_date=START_DATE,
            end_date=END_DATE,
            short_window=short_window,
            long_window=long_window,
            regime_window=REGIME_WINDOW,
            position_size=POSITION_SIZE,
            trading_cost=TRADING_COST,
            initial_capital=INITIAL_CAPITAL
        )

        label = f"MA | {ticker} {short_window}/{long_window}"

    elif strategy_type == "rsi":
        rsi_window = int(get_value(row, "RSI Window", 14))
        oversold_level = int(get_value(row, "Oversold Level", 30))
        overbought_level = int(get_value(row, "Overbought Level", 70))

        data_result, _, _ = run_rsi_backtest(
            ticker=ticker,
            start_date=START_DATE,
            end_date=END_DATE,
            rsi_window=rsi_window,
            oversold_level=oversold_level,
            overbought_level=overbought_level,
            regime_window=REGIME_WINDOW,
            position_size=POSITION_SIZE,
            trading_cost=TRADING_COST,
            initial_capital=INITIAL_CAPITAL
        )

        label = f"RSI | {ticker} {rsi_window} {oversold_level}/{overbought_level}"

    elif strategy_type == "bollinger_bands":
        window = int(get_value(row, "Bollinger Window", 20))
        num_std = float(get_value(row, "Bollinger Std", 2))

        data_result, _, _ = run_bollinger_backtest(
            ticker=ticker,
            start_date=START_DATE,
            end_date=END_DATE,
            window=window,
            num_std=num_std,
            regime_window=REGIME_WINDOW,
            position_size=POSITION_SIZE,
            trading_cost=TRADING_COST,
            initial_capital=INITIAL_CAPITAL
        )

        label = f"Bollinger | {ticker} {window}/{num_std}"

    elif strategy_type == "momentum":
        momentum_window = int(get_value(row, "Momentum Window", 60))

        data_result, _, _ = run_momentum_backtest(
            ticker=ticker,
            start_date=START_DATE,
            end_date=END_DATE,
            momentum_window=momentum_window,
            regime_window=REGIME_WINDOW,
            position_size=POSITION_SIZE,
            trading_cost=TRADING_COST,
            initial_capital=INITIAL_CAPITAL
        )

        label = f"Momentum | {ticker} {momentum_window}"

    elif strategy_type == "breakout":
        breakout_window = int(get_value(row, "Breakout Window", 50))
        exit_window = int(get_value(row, "Exit Window", 20))

        data_result, _, _ = run_breakout_backtest(
            ticker=ticker,
            start_date=START_DATE,
            end_date=END_DATE,
            breakout_window=breakout_window,
            exit_window=exit_window,
            regime_window=REGIME_WINDOW,
            position_size=POSITION_SIZE,
            trading_cost=TRADING_COST,
            initial_capital=INITIAL_CAPITAL
        )

        label = f"Breakout | {ticker} {breakout_window}/{exit_window}"

    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    return label, data_result


def generate_top_strategy_charts(results_path=None, charts_path=None, top_n=3):
    if results_path is None:
        results_path = DEFAULT_RESULTS_PATH
    else:
        results_path = Path(results_path)

    if charts_path is None:
        charts_path = DEFAULT_CHARTS_PATH
    else:
        charts_path = Path(charts_path)

    charts_path.mkdir(parents=True, exist_ok=True)

    batch_results = load_batch_results(results_path)

    top_strategies = get_top_strategies(
        batch_results,
        metric="Sharpe Ratio",
        top_n=top_n
    )

    strategy_data = {}

    print(f"Generating charts for top {top_n} strategies by Sharpe Ratio...")

    for _, row in top_strategies.iterrows():
        label, data_result = rerun_strategy(row)
        strategy_data[label] = data_result
        print(f"Loaded {label}")

    plt.figure(figsize=(14, 7))

    for label, data_result in strategy_data.items():
        equity_curve = INITIAL_CAPITAL * data_result["Strategy_Growth"]
        plt.plot(equity_curve, label=label)

    plt.title(f"Top {top_n} Strategies by Sharpe Ratio - Equity Curves")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)

    equity_chart_file = charts_path / f"top_{top_n}_strategies_equity_curves.png"

    plt.savefig(equity_chart_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Equity chart saved to: {equity_chart_file}")

    plt.figure(figsize=(14, 7))

    for label, data_result in strategy_data.items():
        plt.plot(data_result["Strategy_Drawdown"], label=label)

    plt.title(f"Top {top_n} Strategies by Sharpe Ratio - Drawdown Comparison")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend()
    plt.grid(True)

    drawdown_chart_file = charts_path / f"top_{top_n}_strategies_drawdown.png"

    plt.savefig(drawdown_chart_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Drawdown chart saved to: {drawdown_chart_file}")
    print("\nChart generation completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate quant strategy charts.")
    parser.add_argument("--results-path", type=str, default=None)
    parser.add_argument("--charts-path", type=str, default=None)
    parser.add_argument("--top-n", type=int, default=3)

    args = parser.parse_args()

    generate_top_strategy_charts(
        results_path=args.results_path,
        charts_path=args.charts_path,
        top_n=args.top_n
    )
