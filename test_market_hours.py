
"""
Market Hours Awareness Test

This script tests US market-hours logic.
It does not connect to IBKR.
It does not place orders.
"""

from market_hours import (
    get_now_times,
    check_us_market_hours,
    should_allow_market_order_workflow,
    get_market_hours_status,
)


def main():
    print("Market Hours Awareness Test")
    print("===========================")

    print("\nCurrent Times:")
    print(get_now_times())

    print("\nUS Market Hours:")
    print(check_us_market_hours())

    print("\nOrder Workflow Decision:")
    print(should_allow_market_order_workflow())

    print("\nDashboard Status:")
    print(get_market_hours_status())

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
