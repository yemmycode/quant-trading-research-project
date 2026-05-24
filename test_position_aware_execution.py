
"""
Position-Aware Signal Execution Test

This script tests whether signals are correctly allowed or blocked based on current positions.
It does not connect to IBKR.
It does not place orders.
"""

from position_aware_execution import evaluate_position_aware_signal


def main():
    print("Position-Aware Signal Execution Test")
    print("====================================")

    positions_flat = {}
    positions_long = {
        "SPY": {
            "quantity": 1,
            "avg_price": 500
        }
    }

    buy_signal = {
        "ticker": "SPY",
        "action": "BUY",
        "strategy_label": "Test Strategy"
    }

    sell_signal = {
        "ticker": "SPY",
        "action": "SELL",
        "strategy_label": "Test Strategy"
    }

    hold_signal = {
        "ticker": "SPY",
        "action": "HOLD",
        "strategy_label": "Test Strategy"
    }

    print("\nBUY when flat:")
    print(evaluate_position_aware_signal(buy_signal, positions_flat))

    print("\nBUY when already long:")
    print(evaluate_position_aware_signal(buy_signal, positions_long))

    print("\nSELL when long:")
    print(evaluate_position_aware_signal(sell_signal, positions_long))

    print("\nSELL when flat:")
    print(evaluate_position_aware_signal(sell_signal, positions_flat))

    print("\nHOLD:")
    print(evaluate_position_aware_signal(hold_signal, positions_long))

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
