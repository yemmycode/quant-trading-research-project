
"""
Live Order Dry Run Test

This script tests live order dry-run mode.
It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from live_order_dry_run import run_live_order_dry_run


def main():
    print("Live Order Dry Run Test")
    print("=======================")
    print("No broker connection will be attempted.")
    print("No order will be submitted.")

    dry_run_result = run_live_order_dry_run(
        ticker="SPY",
        side="BUY",
        quantity=1,
        order_type="LMT",
        limit_price=1.00,
        asset_type="etf",
        proposed_position_size=0.01,
        estimated_price=1.00,
        estimated_order_value=1.00,
        current_position_quantity=0,
        manual_confirmation_given=True,
        strategy_name="Dry Run Test",
        signal="BUY"
    )

    print("\nDry Run Result:")
    print(dry_run_result)

    print("\nExpected for now:")
    print("dry_run_passed should likely be False because live mode lock is still locked.")

    print("\nTest completed. No live trading was enabled.")


if __name__ == "__main__":
    main()
