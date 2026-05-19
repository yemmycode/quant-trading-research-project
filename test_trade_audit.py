
"""
Trade Audit Logger Test

This script tests the audit logger.
It does not connect to a broker.
It does not place orders.
"""

from trade_audit import log_audit_event, read_audit_log


def main():
    print("Trade Audit Logger Test")
    print("=======================")

    result = log_audit_event(
        event_type="TEST_EVENT",
        ticker="SPY",
        side="BUY",
        quantity=1,
        order_type="LMT",
        limit_price=1.00,
        strategy_name="manual_test",
        signal="BUY",
        risk_approved=True,
        risk_reason="Approved for test only.",
        manual_confirmation=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        order_id=None,
        broker_status="not_submitted",
        message="Audit logger test event.",
        details={
            "purpose": "Confirm audit logging works.",
            "live_trading": False
        }
    )

    print("Audit event written to:")
    print(result["audit_file"])

    print("\nLatest audit log:")
    df = read_audit_log(limit=5)

    if df.empty:
        print("No audit records found.")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
