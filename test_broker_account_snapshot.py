
"""
Broker Account Snapshot Test

This script tests the broker account snapshot module.
It does not connect to IBKR.
It does not place orders.
"""

from broker_account_snapshot import (
    get_paper_broker_snapshot,
    get_snapshot_summary,
    snapshot_positions_to_dataframe,
)


class DummyPaperBroker:
    def __init__(self):
        self.cash = 9260.83
        self.initial_cash = 10000
        self.positions = {
            "SPY": {
                "quantity": 1,
                "avg_price": 500,
                "latest_price": 500,
            }
        }

    def get_account_info(self):
        return {
            "cash_balance": 9260.83,
            "initial_cash": 10000,
            "total_equity": 10000,
            "total_market_value": 500,
            "total_unrealized_pnl": 0,
            "open_positions": [
                {
                    "ticker": "SPY",
                    "quantity": 1,
                    "avg_price": 500,
                    "latest_price": 500,
                    "market_value": 500,
                    "unrealized_pnl": 0,
                }
            ],
            "price_warnings": []
        }


def main():
    print("Broker Account Snapshot Test")
    print("============================")

    broker = DummyPaperBroker()

    snapshot = get_paper_broker_snapshot(broker)

    print("\nSnapshot:")
    print(snapshot)

    print("\nSummary:")
    print(get_snapshot_summary(snapshot))

    print("\nPositions DataFrame:")
    print(snapshot_positions_to_dataframe(snapshot).to_string(index=False))

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
