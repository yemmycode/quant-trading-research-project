
"""
Fill and Slippage Tracker Test

This script tests fill recording and slippage calculation.
It does not connect to IBKR.
It does not place orders.
"""

from fill_slippage_tracker import (
    calculate_slippage,
    record_order_fill,
    record_fill_from_broker_response,
    read_order_fills,
    summarize_slippage,
    get_fill_slippage_status,
)


def main():
    print("Fill and Slippage Tracker Test")
    print("==============================")

    print("\nBUY fill worse than reference:")
    print(calculate_slippage("BUY", reference_price=500, fill_price=501))

    print("\nSELL fill worse than reference:")
    print(calculate_slippage("SELL", reference_price=500, fill_price=499))

    fill_result = record_order_fill(
        order_key="test-order-001",
        broker_order_id="paper-001",
        ticker="SPY",
        side="BUY",
        order_type="LMT",
        submitted_limit_price=501,
        reference_price=500,
        fill_price=501,
        fill_quantity=1,
        broker_status="filled",
        details={"test": True}
    )

    print("\nRecorded fill:")
    print(fill_result)

    broker_response = {
        "order_id": "paper-002",
        "ticker": "SPY",
        "side": "SELL",
        "order_type": "LMT",
        "limit_price": 499,
        "reference_price": 500,
        "fill_price": 499,
        "filled_quantity": 1,
        "order_status": "filled"
    }

    response_fill = record_fill_from_broker_response(
        broker_response=broker_response,
        order_key="test-order-002"
    )

    print("\nRecorded fill from broker response:")
    print(response_fill)

    print("\nRecent fills:")
    print(read_order_fills(limit=10).to_string(index=False))

    print("\nSlippage summary:")
    print(summarize_slippage())

    print("\nTracker status:")
    print(get_fill_slippage_status())

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
