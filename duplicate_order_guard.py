
"""
Duplicate Order Guard

This module prevents duplicate or repeated order actions.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from datetime import datetime, timedelta
import pandas as pd

from order_state_manager import (
    initialize_order_state_tables,
    read_order_current_states,
    read_order_state_events,
    TERMINAL_ORDER_STATES,
)


ACTIVE_ORDER_STATES = [
    "proposed",
    "risk_checked",
    "approved",
    "submitted",
    "acknowledged",
    "partially_filled",
    "cancel_requested",
]


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().upper()


def get_active_orders_for_ticker(ticker=None, side=None):
    """
    Return active non-terminal orders for a ticker/side.
    """

    initialize_order_state_tables()

    df = read_order_current_states(limit=100000)

    if df.empty:
        return df

    active_df = df[~df["current_state"].isin(TERMINAL_ORDER_STATES)].copy()

    if ticker:
        active_df = active_df[
            active_df["ticker"].astype(str).str.upper() == normalize_text(ticker)
        ]

    if side:
        active_df = active_df[
            active_df["side"].astype(str).str.upper() == normalize_text(side)
        ]

    return active_df


def has_active_duplicate_order(ticker, side=None):
    """
    Check whether there is an active order for the same ticker and optional side.
    """

    active_df = get_active_orders_for_ticker(ticker=ticker, side=side)

    return not active_df.empty


def check_duplicate_order(
    ticker,
    side,
    proposed_order=None,
    signal_id=None,
    strategy_name=None,
    lookback_minutes=1440,
):
    """
    Check whether a proposed order appears to be a duplicate.

    Duplicate blockers:
    1. Active non-terminal order exists for same ticker and side.
    2. Active non-terminal order exists for same ticker in any side.
    3. Similar order was created recently within lookback window.
    """

    ticker = normalize_text(ticker)
    side = normalize_text(side)

    blockers = []
    warnings = []

    active_same_side = get_active_orders_for_ticker(ticker=ticker, side=side)

    if not active_same_side.empty:
        blockers.append(
            f"Active {side} order already exists for {ticker}."
        )

    active_same_ticker = get_active_orders_for_ticker(ticker=ticker)

    if not active_same_ticker.empty:
        active_other_side = active_same_ticker[
            active_same_ticker["side"].astype(str).str.upper() != side
        ]

        if not active_other_side.empty:
            warnings.append(
                f"Active order exists for {ticker} on the opposite side. Review before proceeding."
            )

    recent_duplicate_found = False

    events_df = read_order_state_events(limit=100000)

    if not events_df.empty:
        events_df = events_df.copy()

        if "created_at" in events_df.columns:
            events_df["created_at_dt"] = pd.to_datetime(
                events_df["created_at"],
                errors="coerce"
            )

            cutoff_time = datetime.now() - timedelta(minutes=int(lookback_minutes))

            recent_events = events_df[
                events_df["created_at_dt"] >= cutoff_time
            ].copy()

            if not recent_events.empty:
                recent_same = recent_events[
                    (recent_events["ticker"].astype(str).str.upper() == ticker)
                    & (recent_events["side"].astype(str).str.upper() == side)
                ]

                if not recent_same.empty:
                    recent_duplicate_found = True
                    warnings.append(
                        f"Recent {side} order activity found for {ticker} within {lookback_minutes} minutes."
                    )

    duplicate_blocked = len(blockers) > 0

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ticker": ticker,
        "side": side,
        "duplicate_blocked": duplicate_blocked,
        "allowed": not duplicate_blocked,
        "blockers": blockers,
        "warnings": warnings,
        "recent_duplicate_found": recent_duplicate_found,
        "active_same_side_count": len(active_same_side),
        "active_same_ticker_count": len(active_same_ticker),
        "signal_id": signal_id,
        "strategy_name": strategy_name,
        "proposed_order": proposed_order or {},
    }


def check_duplicate_order_from_proposal(proposal, signal_id=None, lookback_minutes=1440):
    """
    Check duplicate status using an order proposal dictionary.
    """

    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a dictionary.")

    ticker = proposal.get("ticker")
    side = proposal.get("side")

    if not ticker:
        raise ValueError("proposal must contain ticker.")

    if not side:
        raise ValueError("proposal must contain side.")

    return check_duplicate_order(
        ticker=ticker,
        side=side,
        proposed_order=proposal,
        signal_id=signal_id,
        strategy_name=proposal.get("strategy_label"),
        lookback_minutes=lookback_minutes,
    )


def get_duplicate_guard_status():
    """
    Return duplicate guard status.
    """

    active_orders = get_active_orders_for_ticker()

    if active_orders.empty:
        active_order_count = 0
    else:
        active_order_count = len(active_orders)

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active_order_count": active_order_count,
        "active_order_states": ACTIVE_ORDER_STATES,
        "terminal_order_states": TERMINAL_ORDER_STATES,
    }
