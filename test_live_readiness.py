
"""
Live Readiness Checklist Test

This script tests the live readiness checklist.
It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from live_readiness import (
    read_readiness_state,
    update_readiness_check,
    get_readiness_summary,
    readiness_to_dataframe
)


def main():
    print("Live Trading Readiness Checklist Test")
    print("=====================================")

    print("\nInitial state:")
    print(read_readiness_state())

    print("\nUpdating sample checks...")

    update_readiness_check(
        "risk_manager_tested",
        True,
        "Risk manager broker checks tested successfully."
    )

    update_readiness_check(
        "manual_confirmation_tested",
        True,
        "Manual confirmation workflow tested in paper mode."
    )

    update_readiness_check(
        "no_live_trading_enabled",
        True,
        "Live trading remains disabled."
    )

    summary = get_readiness_summary()

    print("\nSummary:")
    print(summary.get("summary"))
    print("Overall Status:", summary.get("overall_status"))
    print("Live Trading Recommended:", summary.get("live_trading_recommended"))
    print("Final Review Note:", summary.get("final_review_note"))

    print("\nChecklist DataFrame:")
    df = readiness_to_dataframe()
    print(df.to_string(index=False))

    print("\nReadiness checklist test completed.")


if __name__ == "__main__":
    main()
