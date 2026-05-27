
"""
Trading Control Center Test

This script tests the consolidated pre-trade workflow.
It does not connect to IBKR.
It does not place orders.
"""

from trading_control_center import (
    run_trading_control_center_check,
    get_control_center_step_summary,
)


def main():
    print("Trading Control Center Test")
    print("===========================")

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
    print(result["final_decision"])
    print(result["final_message"])

    print("\nBlockers:")
    for blocker in result["blockers"]:
        print("-", blocker)

    print("\nWarnings:")
    for warning in result["warnings"]:
        print("-", warning)

    print("\nStep summary:")
    for row in get_control_center_step_summary(result):
        print(row)

    print("\nNo broker connection was attempted.")
    print("No order was submitted.")


if __name__ == "__main__":
    main()
