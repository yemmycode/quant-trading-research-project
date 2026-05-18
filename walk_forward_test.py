
import sys
from pathlib import Path
import argparse
import pandas as pd

# Project paths
PROJECT_PATH = Path(r"C:\\Users\\yemi\\OneDrive\\Desktop\\quant_trading_project")
STRATEGIES_PATH = PROJECT_PATH / "strategies"
DEFAULT_RESULTS_PATH = PROJECT_PATH / "results"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(STRATEGIES_PATH) not in sys.path:
    sys.path.append(str(STRATEGIES_PATH))

from moving_average_strategy import run_backtest
from rsi_strategy import run_rsi_backtest

from config import (
    INITIAL_CAPITAL,
    POSITION_SIZE,
    TRADING_COST,
    REGIME_WINDOW,
    STRATEGIES,
    TICKERS,
    MOVING_AVERAGE_PARAMETER_SETS,
    RSI_PARAMETER_SETS
)


TRAIN_START = "2018-01-01"
TRAIN_END = "2021-12-31"

TEST_START = "2022-01-01"
TEST_END = "2025-01-01"


def run_all_strategies_for_period(start_date, end_date):
    all_results = []

    if "moving_average" in STRATEGIES:
        for ticker in TICKERS:
            for params in MOVING_AVERAGE_PARAMETER_SETS:
                short_window = params["short_window"]
                long_window = params["long_window"]

                print(f"Training/Test MA: {ticker} {short_window}/{long_window}")

                try:
                    _, summary_result, trade_log = run_backtest(
                        ticker=ticker,
                        start_date=start_date,
                        end_date=end_date,
                        short_window=short_window,
                        long_window=long_window,
                        regime_window=REGIME_WINDOW,
                        position_size=POSITION_SIZE,
                        trading_cost=TRADING_COST,
                        initial_capital=INITIAL_CAPITAL
                    )

                    row = summary_result[
                        summary_result["Strategy"] == "Quant Strategy"
                    ].copy()

                    row["Strategy Type"] = "moving_average"
                    row["Period Start"] = start_date
                    row["Period End"] = end_date

                    all_results.append(row)

                except Exception as e:
                    print(f"Failed MA {ticker} {short_window}/{long_window}: {e}")

    if "rsi" in STRATEGIES:
        for ticker in TICKERS:
            for params in RSI_PARAMETER_SETS:
                rsi_window = params["rsi_window"]
                oversold_level = params["oversold_level"]
                overbought_level = params["overbought_level"]

                print(
                    f"Training/Test RSI: {ticker} "
                    f"{rsi_window} {oversold_level}/{overbought_level}"
                )

                try:
                    _, summary_result, trade_log = run_rsi_backtest(
                        ticker=ticker,
                        start_date=start_date,
                        end_date=end_date,
                        rsi_window=rsi_window,
                        oversold_level=oversold_level,
                        overbought_level=overbought_level,
                        regime_window=REGIME_WINDOW,
                        position_size=POSITION_SIZE,
                        trading_cost=TRADING_COST,
                        initial_capital=INITIAL_CAPITAL
                    )

                    row = summary_result[
                        summary_result["Strategy"] == "RSI Strategy"
                    ].copy()

                    row["Strategy Type"] = "rsi"
                    row["Period Start"] = start_date
                    row["Period End"] = end_date

                    all_results.append(row)

                except Exception as e:
                    print(
                        f"Failed RSI {ticker} {rsi_window} "
                        f"{oversold_level}/{overbought_level}: {e}"
                    )

    if not all_results:
        raise ValueError("No successful strategy tests completed.")

    results = pd.concat(all_results, ignore_index=True)

    numeric_cols = [
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

    for col in numeric_cols:
        if col in results.columns:
            results[col] = results[col].round(2)

    return results


def rerun_selected_strategy(best_row, start_date, end_date):
    ticker = best_row["Ticker"]
    strategy_type = best_row["Strategy Type"]

    if strategy_type == "moving_average":
        short_window = int(best_row["Short Window"])
        long_window = int(best_row["Long Window"])

        data_result, summary_result, trade_log = run_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            short_window=short_window,
            long_window=long_window,
            regime_window=REGIME_WINDOW,
            position_size=POSITION_SIZE,
            trading_cost=TRADING_COST,
            initial_capital=INITIAL_CAPITAL
        )

        row = summary_result[
            summary_result["Strategy"] == "Quant Strategy"
        ].copy()

        row["Strategy Type"] = "moving_average"

    elif strategy_type == "rsi":
        rsi_window = int(best_row["RSI Window"])
        oversold_level = int(best_row["Oversold Level"])
        overbought_level = int(best_row["Overbought Level"])

        data_result, summary_result, trade_log = run_rsi_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            rsi_window=rsi_window,
            oversold_level=oversold_level,
            overbought_level=overbought_level,
            regime_window=REGIME_WINDOW,
            position_size=POSITION_SIZE,
            trading_cost=TRADING_COST,
            initial_capital=INITIAL_CAPITAL
        )

        row = summary_result[
            summary_result["Strategy"] == "RSI Strategy"
        ].copy()

        row["Strategy Type"] = "rsi"

    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    row["Period Start"] = start_date
    row["Period End"] = end_date

    return data_result, row


def run_walk_forward_test(results_path=None):
    if results_path is None:
        results_path = DEFAULT_RESULTS_PATH
    else:
        results_path = Path(results_path)

    results_path.mkdir(parents=True, exist_ok=True)

    print("\nRunning training period tests...")
    training_results = run_all_strategies_for_period(TRAIN_START, TRAIN_END)

    best_training_strategy = training_results.sort_values(
        by="Sharpe Ratio",
        ascending=False
    ).iloc[0]

    print("\nBest strategy selected from training period:")
    print(best_training_strategy)

    print("\nRunning selected strategy on testing period...")
    testing_data, testing_result = rerun_selected_strategy(
        best_training_strategy,
        TEST_START,
        TEST_END
    )

    training_file = results_path / "walk_forward_training_results.csv"
    testing_file = results_path / "walk_forward_testing_result.csv"
    testing_data_file = results_path / "walk_forward_testing_data.csv"

    training_results.to_csv(training_file, index=False)
    testing_result.to_csv(testing_file, index=False)
    testing_data.to_csv(testing_data_file)

    comparison = pd.concat(
        [
            best_training_strategy.to_frame().T.assign(Evaluation="Training Winner"),
            testing_result.assign(Evaluation="Out-of-Sample Test")
        ],
        ignore_index=True
    )

    comparison_file = results_path / "walk_forward_comparison.csv"
    comparison.to_csv(comparison_file, index=False)

    print("\nWalk-forward test completed successfully.")
    print(f"Training results saved to: {training_file}")
    print(f"Testing result saved to: {testing_file}")
    print(f"Comparison saved to: {comparison_file}")

    return training_results, testing_result, comparison


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run walk-forward quant strategy test.")
    parser.add_argument(
        "--results-path",
        type=str,
        default=None,
        help="Optional folder where walk-forward result files should be saved."
    )

    args = parser.parse_args()

    run_walk_forward_test(results_path=args.results_path)
