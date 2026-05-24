
"""
Snapshot Position-Aware Execution Test

This script tests position-aware logic using broker account snapshots.
It does not connect to IBKR.
It does not place orders.
"""

from position_aware_execution import evaluate_position_aware_proposal_with_snapshot


def main():
    print("Snapshot Position-Aware Execution Test")
    print("======================================")

    flat_snapshot = {
        "snapshot_available": True,
        "timestamp": "2026-05-24 10:00:00",
        "cash_balance": 10000,
        "total_equity": 10000,
        "position_count": 0,
        "positions": [],
        "environment_status": "IBKR_PAPER_ORDER_TEST"
    }

    long_snapshot = {
        "snapshot_available": True,
        "timestamp": "2026-05-24 10:00:00",
        "cash_balance": 9500,
        "total_equity": 10000,
        "position_count": 1,
        "positions": [
            {
                "ticker": "SPY",
                "quantity": 1,
                "avg_price": 500,
                "latest_price": 500,
                "market_value": 500,
                "unrealized_pnl": 0
            }
        ],
        "environment_status": "IBKR_PAPER_ORDER_TEST"
    }

    buy_proposal = {
        "ticker": "SPY",
        "side": "BUY",
        "quantity": 1,
        "order_type": "LMT",
        "limit_price": 499,
        "actionable": True
    }

    sell_proposal = {
        "ticker": "SPY",
        "side": "SELL",
        "quantity": 1,
        "order_type": "LMT",
        "limit_price": 501,
        "actionable": True
    }

    print("\nBUY with flat snapshot:")
    print(evaluate_position_aware_proposal_with_snapshot(buy_proposal, flat_snapshot))

    print("\nBUY with long snapshot:")
    print(evaluate_position_aware_proposal_with_snapshot(buy_proposal, long_snapshot))

    print("\nSELL with long snapshot:")
    print(evaluate_position_aware_proposal_with_snapshot(sell_proposal, long_snapshot))

    print("\nSELL with flat snapshot:")
    print(evaluate_position_aware_proposal_with_snapshot(sell_proposal, flat_snapshot))

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
