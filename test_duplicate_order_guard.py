
"""
Duplicate Order Guard Test

This script tests duplicate order protection.
It does not connect to IBKR.
It does not place orders.
"""

from order_state_manager import (
    initialize_order_state_tables,
    create_order_state_from_proposal,
    record_broker_status_update,
)
from duplicate_order_guard import (
    check_duplicate_order_from_proposal,
    get_active_orders_for_ticker,
    get_duplicate_guard_status,
)


def main():
    print("Duplicate Order Guard Test")
    print("==========================")

    initialize_order_state_tables()

    proposal = {
        "ticker": "SPY",
        "side": "BUY",
        "quantity": 1,
        "order_type": "LMT",
        "limit_price": 499.00,
        "estimated_order_value": 499.00,
        "proposal_status": "proposed",
        "actionable": True,
        "reason": "Duplicate guard test proposal."
    }

    state_result = create_order_state_from_proposal(
        proposal=proposal,
        proposal_id=999
    )

    print("\nCreated test active order state:")
    print(state_result)

    duplicate_check = check_duplicate_order_from_proposal(
        proposal=proposal,
        signal_id=999,
        lookback_minutes=1440
    )

    print("\nDuplicate check result:")
    print(duplicate_check)

    active_orders = get_active_orders_for_ticker("SPY", "BUY")

    print("\nActive SPY BUY orders:")
    if active_orders.empty:
        print("None")
    else:
        print(active_orders.to_string(index=False))

    print("\nNow marking test order as cancelled...")

    record_broker_status_update(
        order_key=state_result["order_key"],
        broker_status="Cancelled",
        message="Test order cancelled after duplicate guard test."
    )

    duplicate_check_after_cancel = check_duplicate_order_from_proposal(
        proposal=proposal,
        signal_id=999,
        lookback_minutes=1440
    )

    print("\nDuplicate check after cancellation:")
    print(duplicate_check_after_cancel)

    print("\nDuplicate guard status:")
    print(get_duplicate_guard_status())

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
