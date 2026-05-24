
"""
Broker Account Snapshot Module

This module captures account state snapshots from the current broker environment.

It does not place orders.
It does not enable live trading.
For now, it focuses mainly on the simulated paper broker.
"""

from datetime import datetime
import pandas as pd

from broker_environment import get_environment_recommendation


def normalize_position(position):
    """
    Normalize one position dictionary into a consistent structure.
    """

    if not isinstance(position, dict):
        return {
            "ticker": "",
            "quantity": 0.0,
            "avg_price": 0.0,
            "latest_price": 0.0,
            "market_value": 0.0,
            "unrealized_pnl": 0.0,
        }

    ticker = (
        position.get("ticker")
        or position.get("symbol")
        or position.get("contract_symbol")
        or ""
    )

    quantity = (
        position.get("quantity")
        or position.get("position")
        or position.get("shares")
        or 0.0
    )

    avg_price = (
        position.get("avg_price")
        or position.get("average_price")
        or position.get("avgCost")
        or position.get("entry_price")
        or 0.0
    )

    latest_price = (
        position.get("latest_price")
        or position.get("market_price")
        or position.get("last_price")
        or avg_price
        or 0.0
    )

    try:
        quantity = float(quantity)
    except Exception:
        quantity = 0.0

    try:
        avg_price = float(avg_price)
    except Exception:
        avg_price = 0.0

    try:
        latest_price = float(latest_price)
    except Exception:
        latest_price = avg_price

    market_value = position.get("market_value")

    if market_value is None:
        market_value = quantity * latest_price

    try:
        market_value = float(market_value)
    except Exception:
        market_value = 0.0

    unrealized_pnl = position.get("unrealized_pnl")

    if unrealized_pnl is None:
        unrealized_pnl = (latest_price - avg_price) * quantity

    try:
        unrealized_pnl = float(unrealized_pnl)
    except Exception:
        unrealized_pnl = 0.0

    return {
        "ticker": str(ticker).upper().strip(),
        "quantity": quantity,
        "avg_price": avg_price,
        "latest_price": latest_price,
        "market_value": market_value,
        "unrealized_pnl": unrealized_pnl,
    }


def normalize_positions(positions):
    """
    Normalize list/dict positions into a clean list.
    """

    if not positions:
        return []

    normalized = []

    if isinstance(positions, dict):
        for ticker, position in positions.items():
            if isinstance(position, dict):
                item = position.copy()
                item["ticker"] = item.get("ticker") or ticker
            else:
                item = {
                    "ticker": ticker,
                    "quantity": position,
                }

            normalized.append(normalize_position(item))

    elif isinstance(positions, list):
        for position in positions:
            normalized.append(normalize_position(position))

    return normalized


def get_paper_broker_snapshot(paper_broker=None):
    """
    Capture account snapshot from the simulated paper broker.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if paper_broker is None:
        return {
            "snapshot_available": False,
            "snapshot_type": "paper_broker",
            "timestamp": timestamp,
            "reason": "No paper broker object found in session state.",
            "cash_balance": 0.0,
            "initial_cash": 0.0,
            "total_equity": 0.0,
            "total_market_value": 0.0,
            "total_unrealized_pnl": 0.0,
            "position_count": 0,
            "positions": [],
            "price_warnings": [],
        }

    try:
        if hasattr(paper_broker, "get_account_info"):
            account_info = paper_broker.get_account_info()
        else:
            account_info = {}

    except Exception as e:
        return {
            "snapshot_available": False,
            "snapshot_type": "paper_broker",
            "timestamp": timestamp,
            "reason": f"Could not read paper broker account info: {type(e).__name__}: {e}",
            "cash_balance": 0.0,
            "initial_cash": 0.0,
            "total_equity": 0.0,
            "total_market_value": 0.0,
            "total_unrealized_pnl": 0.0,
            "position_count": 0,
            "positions": [],
            "price_warnings": [],
        }

    positions = (
        account_info.get("open_positions")
        or account_info.get("positions")
        or getattr(paper_broker, "positions", {})
        or []
    )

    normalized_positions = normalize_positions(positions)

    cash_balance = (
        account_info.get("cash_balance")
        or account_info.get("cash")
        or getattr(paper_broker, "cash", 0.0)
        or 0.0
    )

    initial_cash = (
        account_info.get("initial_cash")
        or account_info.get("starting_cash")
        or getattr(paper_broker, "initial_cash", None)
        or getattr(paper_broker, "starting_cash", None)
        or 0.0
    )

    total_market_value = account_info.get("total_market_value")

    if total_market_value is None:
        total_market_value = sum(p["market_value"] for p in normalized_positions)

    total_unrealized_pnl = account_info.get("total_unrealized_pnl")

    if total_unrealized_pnl is None:
        total_unrealized_pnl = sum(p["unrealized_pnl"] for p in normalized_positions)

    try:
        cash_balance = float(cash_balance)
    except Exception:
        cash_balance = 0.0

    try:
        initial_cash = float(initial_cash)
    except Exception:
        initial_cash = 0.0

    try:
        total_market_value = float(total_market_value)
    except Exception:
        total_market_value = 0.0

    try:
        total_unrealized_pnl = float(total_unrealized_pnl)
    except Exception:
        total_unrealized_pnl = 0.0

    total_equity = account_info.get("total_equity") or account_info.get("equity")

    if total_equity is None:
        total_equity = cash_balance + total_market_value

    try:
        total_equity = float(total_equity)
    except Exception:
        total_equity = cash_balance + total_market_value

    return {
        "snapshot_available": True,
        "snapshot_type": "paper_broker",
        "timestamp": timestamp,
        "cash_balance": cash_balance,
        "initial_cash": initial_cash,
        "total_equity": total_equity,
        "total_market_value": total_market_value,
        "total_unrealized_pnl": total_unrealized_pnl,
        "position_count": len(normalized_positions),
        "positions": normalized_positions,
        "price_warnings": account_info.get("price_warnings", []),
        "raw_account_info": account_info,
    }


def get_broker_account_snapshot(paper_broker=None):
    """
    Return a broker account snapshot with environment information.
    """

    environment = get_environment_recommendation()
    snapshot = get_paper_broker_snapshot(paper_broker=paper_broker)

    snapshot["environment_status"] = environment.get("status")
    snapshot["environment_safe"] = environment.get("safe")
    snapshot["environment_message"] = environment.get("message")
    snapshot["environment_recommendation"] = environment.get("recommendation")

    return snapshot


def snapshot_positions_to_dataframe(snapshot):
    """
    Convert snapshot positions to DataFrame.
    """

    positions = snapshot.get("positions", [])

    if not positions:
        return pd.DataFrame(
            columns=[
                "ticker",
                "quantity",
                "avg_price",
                "latest_price",
                "market_value",
                "unrealized_pnl",
            ]
        )

    return pd.DataFrame(positions)


def get_snapshot_summary(snapshot):
    """
    Return compact snapshot summary for dashboard display.
    """

    return {
        "snapshot_available": snapshot.get("snapshot_available", False),
        "timestamp": snapshot.get("timestamp"),
        "snapshot_type": snapshot.get("snapshot_type"),
        "cash_balance": snapshot.get("cash_balance", 0.0),
        "initial_cash": snapshot.get("initial_cash", 0.0),
        "total_equity": snapshot.get("total_equity", 0.0),
        "total_market_value": snapshot.get("total_market_value", 0.0),
        "total_unrealized_pnl": snapshot.get("total_unrealized_pnl", 0.0),
        "position_count": snapshot.get("position_count", 0),
        "environment_status": snapshot.get("environment_status"),
        "environment_safe": snapshot.get("environment_safe"),
    }
