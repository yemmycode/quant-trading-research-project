
import sys
from pathlib import Path
import argparse
import pandas as pd
from datetime import datetime

from database import save_strategy_results

PROJECT_PATH = Path(__file__).resolve().parent
STRATEGIES_PATH = PROJECT_PATH / "strategies"
DEFAULT_RESULTS_PATH = PROJECT_PATH / "results"

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
    REGIME_WINDOW,
    STRATEGIES,
    TICKERS,
    MOVING_AVERAGE_PARAMETER_SETS,
    RSI_PARAMETER_SETS,
    BOLLINGER_PARAMETER_SETS,
    MOMENTUM_PARAMETER_SETS,
    BREAKOUT_PARAMETER_SETS
)


def append_strategy_result(all_results, summary_result, strategy_name):
    """
    Extract the strategy row, ensure it has Strategy Type, and append it.
    """

    strategy_type_map = {
        "Quant Strategy": "moving_average",
        "RSI Strategy": "rsi",
        "Bollinger Bands Strategy": "bollinger_bands",
        "Momentum Strategy": "momentum",
        "Breakout Strategy": "breakout"
    }

    strategy_row = summary_result[
        summary_result["Strategy"] == strategy_name
    ].copy()

    if not strategy_row.empty:
        expected_strategy_type = strategy_type_map.get(strategy_name)

        if "Strategy Type" not in strategy_row.columns:
            strategy_row["Strategy Type"] = expected_strategy_type
        else:
            strategy_row["Strategy Type"] = strategy_row["Strategy Type"].fillna(expected_strategy_type)

        all_results.append(strategy_row)


def run_moving_average_tests(all_results):
    for ticker in TICKERS:
        for params in MOVING_AVERAGE_PARAMETER_SETS:
            short_window = params["short_window"]
            long_window = params["long_window"]

            print(f"Running Moving Average: {ticker} {short_window}/{long_window}")

            try:
                _, summary_result, _ = run_backtest(
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

                append_strategy_result(all_results, summary_result, "Quant Strategy")

            except Exception as e:
                print(f"Failed Moving Average {ticker} {short_window}/{long_window}: {e}")


def run_rsi_tests(all_results):
    for ticker in TICKERS:
        for params in RSI_PARAMETER_SETS:
            rsi_window = params["rsi_window"]
            oversold_level = params["oversold_level"]
            overbought_level = params["overbought_level"]

            print(f"Running RSI: {ticker} {rsi_window} {oversold_level}/{overbought_level}")

            try:
                _, summary_result, _ = run_rsi_backtest(
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

                append_strategy_result(all_results, summary_result, "RSI Strategy")

            except Exception as e:
                print(f"Failed RSI {ticker} {rsi_window}: {e}")


def run_bollinger_tests(all_results):
    for ticker in TICKERS:
        for params in BOLLINGER_PARAMETER_SETS:
            window = params["window"]
            num_std = params["num_std"]

            print(f"Running Bollinger Bands: {ticker} window={window}, std={num_std}")

            try:
                _, summary_result, _ = run_bollinger_backtest(
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

                append_strategy_result(all_results, summary_result, "Bollinger Bands Strategy")

            except Exception as e:
                print(f"Failed Bollinger {ticker} {window}/{num_std}: {e}")


def run_momentum_tests(all_results):
    for ticker in TICKERS:
        for params in MOMENTUM_PARAMETER_SETS:
            momentum_window = params["momentum_window"]

            print(f"Running Momentum: {ticker} window={momentum_window}")

            try:
                _, summary_result, _ = run_momentum_backtest(
                    ticker=ticker,
                    start_date=START_DATE,
                    end_date=END_DATE,
                    momentum_window=momentum_window,
                    regime_window=REGIME_WINDOW,
                    position_size=POSITION_SIZE,
                    trading_cost=TRADING_COST,
                    initial_capital=INITIAL_CAPITAL
                )

                append_strategy_result(all_results, summary_result, "Momentum Strategy")

            except Exception as e:
                print(f"Failed Momentum {ticker} {momentum_window}: {e}")


def run_breakout_tests(all_results):
    for ticker in TICKERS:
        for params in BREAKOUT_PARAMETER_SETS:
            breakout_window = params["breakout_window"]
            exit_window = params["exit_window"]

            print(f"Running Breakout: {ticker} breakout={breakout_window}, exit={exit_window}")

            try:
                _, summary_result, _ = run_breakout_backtest(
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

                append_strategy_result(all_results, summary_result, "Breakout Strategy")

            except Exception as e:
                print(f"Failed Breakout {ticker} {breakout_window}/{exit_window}: {e}")


def run_batch_tests(results_path=None):
    if results_path is None:
        results_path = DEFAULT_RESULTS_PATH
    else:
        results_path = Path(results_path)

    results_path.mkdir(parents=True, exist_ok=True)

    all_results = []

    if "moving_average" in STRATEGIES:
        run_moving_average_tests(all_results)

    if "rsi" in STRATEGIES:
        run_rsi_tests(all_results)

    if "bollinger_bands" in STRATEGIES:
        run_bollinger_tests(all_results)

    if "momentum" in STRATEGIES:
        run_momentum_tests(all_results)

    if "breakout" in STRATEGIES:
        run_breakout_tests(all_results)

    if not all_results:
        raise ValueError("No successful backtests were completed.")

    combined_results = pd.concat(all_results, ignore_index=True)

    columns_to_round = [
        "Position Size",
        "Trading Cost",
        "Total Return (%)",
        "Annual Return (%)",
        "Volatility (%)",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Calmar Ratio",
        "Max Drawdown (%)",
        "Win Rate (%)",
        "Average Win (%)",
        "Average Loss (%)",
        "Profit Factor",
        "Recovery Factor",
        "Final Value (R)"
    ]

    for col in columns_to_round:
        if col in combined_results.columns:
            combined_results[col] = combined_results[col].round(2)

    csv_file = results_path / "batch_test_results.csv"
    excel_file = results_path / "batch_test_results.xlsx"

    combined_results.to_csv(csv_file, index=False)
    combined_results.to_excel(excel_file, index=False)

    run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    db_rows_saved = save_strategy_results(combined_results, run_id=run_id)

    print("\nBatch tests completed successfully.")
    print(f"Database rows saved: {db_rows_saved}")
    print(f"CSV saved to: {csv_file}")
    print(f"Excel saved to: {excel_file}")

    return combined_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch quant strategy tests.")
    parser.add_argument(
        "--results-path",
        type=str,
        default=None,
        help="Optional folder where result files should be saved."
    )

    args = parser.parse_args()

    run_batch_tests(results_path=args.results_path)
