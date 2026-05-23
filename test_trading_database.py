
"""
Trading Database Foundation Test

This script tests the SQLite trading database foundation.
It does not connect to IBKR.
It does not place orders.
"""

from trading_database import (
    initialize_trading_database,
    insert_signal,
    insert_order_proposal,
    insert_audit_event,
    insert_system_event,
    read_table,
    get_database_status
)


def main():
    print("Trading Database Foundation Test")
    print("================================")

    db_file = initialize_trading_database()

    print("\nDatabase initialized:")
    print(db_file)

    signal = {
        "ticker": "SPY",
        "strategy_label": "Moving Average 20/50",
        "action": "BUY",
        "reason": "Test signal only.",
        "latest_close": 500.00,
        "latest_date": "2026-05-23"
    }

    signal_id = insert_signal(signal)
    print("\nInserted signal ID:", signal_id)

    proposal = {
        "ticker": "SPY",
        "side": "BUY",
        "quantity": 1,
        "order_type": "LMT",
        "limit_price": 499.00,
        "estimated_order_value": 499.00,
        "proposal_status": "proposed",
        "actionable": True
    }

    proposal_id = insert_order_proposal(proposal, signal_id=signal_id)
    print("Inserted proposal ID:", proposal_id)

    audit_id = insert_audit_event(
        event_type="DATABASE_TEST",
        message="Testing database audit event.",
        ticker="SPY",
        severity="INFO",
        details={"test": True}
    )
    print("Inserted audit event ID:", audit_id)

    system_event_id = insert_system_event(
        event_type="DATABASE_INITIALIZED",
        component="trading_database",
        status="ok",
        message="Trading database initialized successfully.",
        details={"db_file": db_file}
    )
    print("Inserted system event ID:", system_event_id)

    print("\nDatabase status:")
    print(get_database_status())

    print("\nSignals table:")
    print(read_table("signals", limit=5).to_string(index=False))

    print("\nOrder proposals table:")
    print(read_table("order_proposals", limit=5).to_string(index=False))

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
