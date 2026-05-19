
"""
Risk Manager Emergency Stop Test

This confirms persistent emergency stop blocks broker orders.
No broker connection.
No orders.
"""

from safety_manager import activate_emergency_stop, deactivate_emergency_stop
from risk_manager import create_risk_manager_from_config


def main():
    print("Risk Manager Emergency Stop Test")
    print("===============================")

    risk_manager = create_risk_manager_from_config()

    print("\nActivating persistent emergency stop...")
    activate_emergency_stop(
        reason="Testing risk manager emergency stop block.",
        updated_by="test_risk_emergency_stop.py"
    )

    result = risk_manager.approve_broker_order(
        ticker="SPY",
        side="BUY",
        quantity=1,
        order_type="LMT",
        asset_type="etf",
        proposed_position_size=0.01,
        estimated_price=1.00,
        estimated_order_value=1.00,
        current_position_quantity=0,
        manual_confirmation_given=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print("Approved:", result.approved)
    print("Reason:", result.reason)
    print("Details:", result.details)

    print("\nDeactivating emergency stop...")
    deactivate_emergency_stop(
        reason="Emergency stop test completed.",
        updated_by="test_risk_emergency_stop.py"
    )

    result = risk_manager.approve_broker_order(
        ticker="SPY",
        side="BUY",
        quantity=1,
        order_type="LMT",
        asset_type="etf",
        proposed_position_size=0.01,
        estimated_price=1.00,
        estimated_order_value=1.00,
        current_position_quantity=0,
        manual_confirmation_given=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print("\nAfter deactivation:")
    print("Approved:", result.approved)
    print("Reason:", result.reason)


if __name__ == "__main__":
    main()
