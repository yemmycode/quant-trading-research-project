
"""
Trading Control Center Dry Run Test

This script runs the consolidated workflow as a dry run.
It does not connect to IBKR.
It does not submit orders.
"""

from control_center_dry_run import (
    run_control_center_dry_run,
    read_control_center_dry_runs,
    summarize_control_center_dry_runs,
)


def main():
    print("Trading Control Center Dry Run Test")
    print("===================================")

    result = run_control_center_dry_run(
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

    print("\nDry run record:")
    print(result["dry_run_record"])

    print("\nFinal decision:")
    print(result["control_result"].get("final_decision"))

    print("\nBlockers:")
    for blocker in result["control_result"].get("blockers", []):
        print("-", blocker)

    print("\nRecent dry runs:")
    print(read_control_center_dry_runs(limit=5).to_string(index=False))

    print("\nSummary:")
    print(summarize_control_center_dry_runs())

    print("\nNo broker connection was attempted.")
    print("No order was submitted.")


if __name__ == "__main__":
    main()
