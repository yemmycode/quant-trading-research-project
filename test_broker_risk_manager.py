
"""
Broker Risk Manager Test

This script tests broker-level risk checks.
It does not connect to IBKR.
It does not place orders.
"""

from risk_manager import create_risk_manager_from_config


def print_result(title, result):
    print("\n" + title)
    print("-" * len(title))
    print("Approved:", result.approved)
    print("Reason:", result.reason)
    print("Details:", result.details)


def main():
    risk_manager = create_risk_manager_from_config()

    print("Broker Risk Manager Test")
    print("========================")
    print("No broker connection will be attempted.")
    print("No orders will be placed.")

    # Valid IBKR paper BUY test
    result = risk_manager.approve_broker_order(
        ticker="SPY",
        side="BUY",
        quantity=1,
        order_type="LMT",
        asset_type="etf",
        proposed_position_size=0.05,
        estimated_price=500,
        estimated_order_value=500,
        current_position_quantity=0,
        manual_confirmation_given=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print_result("Valid IBKR Paper BUY", result)

    # Block unsupported ticker
    result = risk_manager.approve_broker_order(
        ticker="TSLA",
        side="BUY",
        quantity=1,
        order_type="LMT",
        asset_type="stock",
        proposed_position_size=0.05,
        estimated_price=200,
        estimated_order_value=200,
        current_position_quantity=0,
        manual_confirmation_given=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print_result("Blocked Unsupported Ticker", result)

    # Block missing manual confirmation
    result = risk_manager.approve_broker_order(
        ticker="SPY",
        side="BUY",
        quantity=1,
        order_type="LMT",
        asset_type="etf",
        proposed_position_size=0.05,
        estimated_price=500,
        estimated_order_value=500,
        current_position_quantity=0,
        manual_confirmation_given=False,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print_result("Blocked Missing Manual Confirmation", result)

    # Block oversized position
    result = risk_manager.approve_broker_order(
        ticker="SPY",
        side="BUY",
        quantity=100,
        order_type="LMT",
        asset_type="etf",
        proposed_position_size=0.50,
        estimated_price=500,
        estimated_order_value=50000,
        current_position_quantity=0,
        manual_confirmation_given=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print_result("Blocked Oversized Position", result)

    # Block short sell attempt
    result = risk_manager.approve_broker_order(
        ticker="SPY",
        side="SELL",
        quantity=1,
        order_type="LMT",
        asset_type="etf",
        proposed_position_size=0.05,
        estimated_price=500,
        estimated_order_value=500,
        current_position_quantity=0,
        manual_confirmation_given=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print_result("Blocked Short Selling", result)

    # Allow SELL only if position exists
    result = risk_manager.approve_broker_order(
        ticker="SPY",
        side="SELL",
        quantity=1,
        order_type="LMT",
        asset_type="etf",
        proposed_position_size=0.05,
        estimated_price=500,
        estimated_order_value=500,
        current_position_quantity=2,
        manual_confirmation_given=True,
        broker_name="ibkr",
        execution_mode="BROKER_PAPER",
        live_order=False
    )

    print_result("Allowed SELL Existing Position", result)


if __name__ == "__main__":
    main()
