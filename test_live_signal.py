
"""
Live Signal Generator Test

This script generates a latest strategy signal.
It does not connect to IBKR.
It does not place orders.
"""

from live_signal import generate_live_signal


def main():
    print("Live Signal Generator Test")
    print("==========================")
    print("No broker connection will be attempted.")
    print("No orders will be placed.")

    signal_result, data, summary, trade_log = generate_live_signal(
        ticker="SPY",
        strategy_name="moving_average",
        start_date="2018-01-01",
        end_date=None,
        initial_capital=10000,
        position_size=0.50,
        trading_cost=0.001,
        regime_window=200,
        short_window=20,
        long_window=50
    )

    print("\nLatest Signal")
    print("-------------")

    for key, value in signal_result.items():
        print(f"{key}: {value}")

    print("\nSummary:")
    print(summary.round(2).to_string(index=False))

    print("\nNo broker order was submitted.")


if __name__ == "__main__":
    main()
