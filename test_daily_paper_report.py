
"""
Daily Paper Trading Report Test

This script generates a daily report from the 30-day paper trading log.
It does not connect to IBKR.
It does not place orders.
"""

from paper_test_tracker import (
    log_paper_test_event,
    generate_daily_paper_report,
    save_daily_paper_report
)


def main():
    print("Daily Paper Trading Report Test")
    print("===============================")

    # Add sample records for test day 1
    log_paper_test_event(
        test_day=1,
        event_type="SIGNAL_REVIEW",
        ticker="SPY",
        strategy_name="Moving Average 20/50",
        signal="HOLD",
        proposal_status="no_order",
        risk_status="not_required",
        manual_decision="reviewed",
        broker_order_status="not_submitted",
        review_note="Reviewed SPY signal. No order required.",
        readiness_status="needs_more_testing"
    )

    log_paper_test_event(
        test_day=1,
        event_type="RISK_BLOCK",
        ticker="SPY",
        strategy_name="Manual Ticket",
        signal="BUY",
        proposal_status="proposed",
        risk_status="blocked",
        manual_decision="rejected",
        broker_order_status="blocked",
        review_note="Risk manager blocked the test order.",
        readiness_status="needs_more_testing"
    )

    report_result = generate_daily_paper_report(test_day=1)

    print("\nReport Result:")
    print(report_result)

    saved = save_daily_paper_report(test_day=1)

    print("\nSaved Report:")
    print(saved["report_file"])

    print("\nDaily paper trading report test completed.")


if __name__ == "__main__":
    main()
