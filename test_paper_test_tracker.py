
"""
30-Day Paper Test Tracker Test

This script tests the paper test tracker.
It does not connect to IBKR.
It does not place orders.
"""

from paper_test_tracker import (
    log_paper_test_event,
    read_paper_test_log,
    summarize_paper_test_log
)


def main():
    print("30-Day Paper Test Tracker Test")
    print("==============================")

    result = log_paper_test_event(
        test_day=1,
        event_type="TEST_NOTE",
        ticker="SPY",
        strategy_name="Moving Average 20/50",
        signal="HOLD",
        proposal_status="no_order",
        risk_status="not_required",
        manual_decision="reviewed",
        broker_order_status="not_submitted",
        review_note="Testing paper trading tracker setup.",
        readiness_status="not_reviewed",
        details={
            "purpose": "Confirm tracker can write and read records."
        }
    )

    print("Tracker event written to:")
    print(result["log_file"])

    print("\nLatest log:")
    df = read_paper_test_log(limit=5)

    if df.empty:
        print("No paper test records found.")
    else:
        print(df.to_string(index=False))

    print("\nSummary:")
    print(summarize_paper_test_log())


if __name__ == "__main__":
    main()
