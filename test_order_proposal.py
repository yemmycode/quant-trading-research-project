
"""
Order Proposal Builder Test

This script converts mock signals into proposed orders.
It does not connect to a broker.
It does not submit orders.
"""

from order_proposal import (
    build_order_proposal_from_signal,
    proposal_to_order_request
)


def print_section(title):
    print("\n" + title)
    print("-" * len(title))


def main():
    print("Order Proposal Builder Test")
    print("===========================")
    print("No broker connection will be attempted.")
    print("No orders will be submitted.")

    buy_signal = {
        "action": "BUY",
        "ticker": "SPY",
        "latest_close": 500,
        "strategy_label": "Moving Average 20/50",
        "reason": "Signal changed from 0 to 1.",
        "latest_date": "2026-05-18"
    }

    print_section("BUY Signal Proposal")

    proposal = build_order_proposal_from_signal(
        signal_result=buy_signal,
        account_equity=10000,
        position_size=0.05,
        order_type="LMT",
        limit_price=499,
        allow_fractional=False,
        current_position_quantity=0,
        asset_type="etf",
        broker_name="ibkr",
        execution_mode="BROKER_PAPER"
    )

    print(proposal)

    if proposal["actionable"]:
        print("\nOrder Request:")
        print(proposal_to_order_request(proposal))

    hold_signal = {
        "action": "HOLD",
        "ticker": "SPY",
        "latest_close": 500,
        "strategy_label": "Moving Average 20/50",
        "reason": "Signal remains invested.",
        "latest_date": "2026-05-18"
    }

    print_section("HOLD Signal Proposal")

    proposal = build_order_proposal_from_signal(
        signal_result=hold_signal,
        account_equity=10000,
        position_size=0.05,
        order_type="LMT",
        limit_price=499,
        allow_fractional=False,
        current_position_quantity=1,
        asset_type="etf",
        broker_name="ibkr",
        execution_mode="BROKER_PAPER"
    )

    print(proposal)

    sell_signal = {
        "action": "SELL",
        "ticker": "SPY",
        "latest_close": 500,
        "strategy_label": "Moving Average 20/50",
        "reason": "Signal changed from 1 to 0.",
        "latest_date": "2026-05-18"
    }

    print_section("SELL Signal With Existing Position")

    proposal = build_order_proposal_from_signal(
        signal_result=sell_signal,
        account_equity=10000,
        position_size=0.05,
        order_type="LMT",
        limit_price=501,
        allow_fractional=False,
        current_position_quantity=2,
        asset_type="etf",
        broker_name="ibkr",
        execution_mode="BROKER_PAPER"
    )

    print(proposal)

    print_section("SELL Signal Without Existing Position")

    proposal = build_order_proposal_from_signal(
        signal_result=sell_signal,
        account_equity=10000,
        position_size=0.05,
        order_type="LMT",
        limit_price=501,
        allow_fractional=False,
        current_position_quantity=0,
        asset_type="etf",
        broker_name="ibkr",
        execution_mode="BROKER_PAPER"
    )

    print(proposal)

    print("\nOrder proposal tests completed.")


if __name__ == "__main__":
    main()
