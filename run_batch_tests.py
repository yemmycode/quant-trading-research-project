
import sys
from pathlib import Path
import argparse
import pandas as pd

# Project paths
PROJECT_PATH = Path(r"C:\Users\yemi\OneDrive\Desktop\quant_trading_project")
STRATEGIES_PATH = PROJECT_PATH / "strategies"
DEFAULT_RESULTS_PATH = PROJECT_PATH / "results"

# Add project folder and strategies folder to Python path
if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(STRATEGIES_PATH) not in sys.path:
    sys.path.append(str(STRATEGIES_PATH))

# Import strategy functions
from moving_average_strategy import run_backtest
from rsi_strategy import run_rsi_backtest

# Import settings from config.py
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
    RSI_PARAMETER_SETS
)


def run_moving_average_tests(all_results):
    """
    Run moving-average strategy tests.
    """

    for ticker in TICKERS:
        for params in MOVING_AVERAGE_PARAMETER_SETS:
            short_window = params["short_window"]
            long_window = params["long_window"]

            print(f"Running Moving Average Strategy: {ticker} {short_window}/{long_window}...")

            try:
                data_result, summary_result = run_backtest(
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

                strategy_row = summary_result[
                    summary_result["Strategy"] == "Quant Strategy"
                ].copy()

                strategy_row["Strategy Type"] = "moving_average"
                all_results.append(strategy_row)

            except Exception as e:
                print(f"Failed Moving Average: {ticker} {short_window}/{long_window}")
                print(f"Error: {e}")


def run_rsi_tests(all_results):
    """
    Run RSI strategy tests.
    """

    for ticker in TICKERS:
        for params in RSI_PARAMETER_SETS:
            rsi_window = params["rsi_window"]
            oversold_level = params["oversold_level"]
            overbought_level = params["overbought_level"]

            print(
                f"Running RSI Strategy: {ticker} "
                f"RSI {rsi_window}, {oversold_level}/{overbought_level}..."
            )

            try:
                data_result, summary_result = run_rsi_backtest(
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

                strategy_row = summary_result[
                    summary_result["Strategy"] == "RSI Strategy"
                ].copy()

                strategy_row["Strategy Type"] = "rsi"
                all_results.append(strategy_row)

            except Exception as e:
                print(
                    f"Failed RSI: {ticker} RSI {rsi_window}, "
                    f"{oversold_level}/{overbought_level}"
                )
                print(f"Error: {e}")


def run_batch_tests(results_path=None):
    """
    Run selected strategies using settings from config.py.
    """

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

    if not all_results:
        raise ValueError("No successful backtests were completed.")

    combined_results = pd.concat(all_results, ignore_index=True)

    columns_to_round = [
        "Position Size",
        "Trading Cost",
        "Total Return (%)",
        "Volatility (%)",
        "Sharpe Ratio",
        "Max Drawdown (%)",
        "Final Value (R)"
    ]

    for col in columns_to_round:
        if col in combined_results.columns:
            combined_results[col] = combined_results[col].round(2)

    csv_file = results_path / "batch_test_results.csv"
    excel_file = results_path / "batch_test_results.xlsx"

    combined_results.to_csv(csv_file, index=False)
    combined_results.to_excel(excel_file, index=False)

    print("\nBatch tests completed successfully.")
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
