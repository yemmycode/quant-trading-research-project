
"""
Trading Control Center Database Logging Test

This script tests whether Trading Control Center runs are saved to SQLite.
It does not connect to IBKR.
It does not place orders.
"""

from trading_control_center import run_trading_control_center_check
from trading_database import (
    read_trading_control_center_runs,
    summarize_trading_control_center_runs,
)


def main():
    print("Trading Control Center Logging Test")
    print("===================================")

    result = run_trading_control_center_check(
        ticker="SPY",
        strategy_name="moving_average",
        short_window=20,
        long_window=50,
        quantity=1,
        order_type="LMT",
        limit_price=None,
        paper_broker=None,
        allow_after_hours=False,
    )

    print("\nFinal decision:")
    print(result.get("final_decision"))

    print("\nDatabase logged:")
    print(result.get("database_logged"))

    print("\nDatabase run ID:")
    print(result.get("database_run_id"))

    if result.get("database_error"):
        print("\nDatabase error:")
        print(result.get("database_error"))

    print("\nRecent Trading Control Center runs:")
    print(read_trading_control_center_runs(limit=5).to_string(index=False))

    print("\nSummary:")
    print(summarize_trading_control_center_runs())

    print("\nNo broker connection was attempted.")
    print("No order was submitted.")


if __name__ == "__main__":
    main()
