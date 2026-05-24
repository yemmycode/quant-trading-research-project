
"""
Unified Order State Manager Test

This script tests order lifecycle state tracking.
It does not connect to IBKR.
It does not place orders.
"""

from order_state_manager import (
    initialize_order_state_tables,
    create_order_state_from_proposal,
    record_risk_check_state,
    record_broker_submission_state,
    record_broker_status_update,
    read_order_current_states,
    read_order_state_events,
    get_order_state_manager_status
)


def main():
    print("Unified Order State Manager Test")
    print("================================")

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
        "reason": "Test proposal created."
    }

    result = create_order_state_from_proposal(
        proposal=proposal,
        proposal_id=1
    )

    print("\nProposal state result:")
    print(result)

    order_key = result["order_key"]

    risk_result = record_risk_check_state(
        order_key=order_key,
        risk_approved=True,
        risk_reason="Risk check approved for test.",
        details={"test": True}
    )

    print("\nRisk state result:")
    print(risk_result)

    broker_response = {
        "broker_name": "ibkr",
        "execution_mode": "BROKER_PAPER",
        "ticker": "SPY",
        "side": "BUY",
        "quantity": 1,
        "order_type": "LMT",
        "limit_price": 499.00,
        "order_id": "test-order-001",
        "order_status": "Submitted"
    }

    submitted_result = record_broker_submission_state(
        order_key=order_key,
        broker_response=broker_response,
        broker_order_row_id=1
    )

    print("\nSubmitted state result:")
    print(submitted_result)

    status_update = record_broker_status_update(
        order_key=order_key,
        broker_status="Cancelled",
        message="Test order cancelled."
    )

    print("\nBroker status update result:")
    print(status_update)

    print("\nCurrent states:")
    print(read_order_current_states(limit=10).to_string(index=False))

    print("\nState events:")
    print(read_order_state_events(order_key=order_key, limit=20).to_string(index=False))

    print("\nManager status:")
    print(get_order_state_manager_status())

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
