
"""
Weekly Paper Trading Review Test

This script generates a weekly review from the 30-day paper trading log.
It does not connect to IBKR.
It does not place orders.
"""

from paper_test_tracker import (
    log_paper_test_event,
    generate_weekly_paper_review,
    save_weekly_paper_review
)


def main():
    print("Weekly Paper Trading Review Test")
    print("================================")

    # Add sample records for week 1
    log_paper_test_event(
        test_day=2,
        event_type="SIGNAL_REVIEW",
        ticker="SPY",
        strategy_name="Moving Average 20/50",
        signal="HOLD",
        proposal_status="no_order",
        risk_status="not_required",
        manual_decision="reviewed",
        broker_order_status="not_submitted",
        review_note="Weekly review sample: signal reviewed.",
        readiness_status="needs_more_testing"
    )

    log_paper_test_event(
        test_day=3,
        event_type="PAPER_ORDER_SUBMITTED",
        ticker="SPY",
        strategy_name="Moving Average 20/50",
        signal="BUY",
        proposal_status="proposed",
        risk_status="approved",
        manual_decision="approved",
        broker_order_status="submitted",
        order_id="sample-001",
        review_note="Weekly review sample: paper order submitted.",
        readiness_status="needs_more_testing"
    )

    review_result = generate_weekly_paper_review(week_number=1)

    print("\nWeekly Review Result:")
    print(review_result)

    saved = save_weekly_paper_review(week_number=1)

    print("\nSaved Weekly Review:")
    print(saved["review_file"])

    print("\nWeekly paper trading review test completed.")


if __name__ == "__main__":
    main()
