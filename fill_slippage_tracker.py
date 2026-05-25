
"""
Fill and Slippage Tracker

This module records order fills and calculates slippage.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from datetime import datetime
import pandas as pd

from trading_database import (
    initialize_trading_database,
    get_database_connection,
    safe_json
)


def safe_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def initialize_fill_slippage_tables():
    """
    Create fill and slippage tracking tables.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_fills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            order_key TEXT,
            broker_order_id TEXT,
            ticker TEXT,
            side TEXT,
            order_type TEXT,
            submitted_limit_price REAL,
            reference_price REAL,
            fill_price REAL,
            fill_quantity REAL,
            fill_value REAL,
            slippage_amount REAL,
            slippage_pct REAL,
            slippage_status TEXT,
            broker_status TEXT,
            raw_fill_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slippage_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            ticker TEXT,
            side TEXT,
            fill_count INTEGER,
            total_fill_quantity REAL,
            average_fill_price REAL,
            average_slippage_pct REAL,
            worst_slippage_pct REAL,
            best_slippage_pct REAL,
            raw_summary_json TEXT
        )
    """)

    conn.commit()
    conn.close()

    return True


def calculate_slippage(side, reference_price, fill_price):
    """
    Calculate slippage amount and percentage.

    For BUY:
    - Positive slippage means fill was worse/higher than reference.
    - Negative slippage means fill was better/lower than reference.

    For SELL:
    - Positive slippage means fill was worse/lower than reference.
    - Negative slippage means fill was better/higher than reference.
    """

    side = str(side or "").upper().strip()
    reference_price = safe_float(reference_price)
    fill_price = safe_float(fill_price)

    if reference_price is None or reference_price <= 0:
        return {
            "slippage_amount": None,
            "slippage_pct": None,
            "slippage_status": "missing_reference_price",
        }

    if fill_price is None or fill_price <= 0:
        return {
            "slippage_amount": None,
            "slippage_pct": None,
            "slippage_status": "missing_fill_price",
        }

    if side == "BUY":
        slippage_amount = fill_price - reference_price
    elif side == "SELL":
        slippage_amount = reference_price - fill_price
    else:
        slippage_amount = fill_price - reference_price

    slippage_pct = slippage_amount / reference_price

    if slippage_pct > 0:
        slippage_status = "worse_than_reference"
    elif slippage_pct < 0:
        slippage_status = "better_than_reference"
    else:
        slippage_status = "at_reference"

    return {
        "slippage_amount": slippage_amount,
        "slippage_pct": slippage_pct,
        "slippage_status": slippage_status,
    }


def record_order_fill(
    order_key=None,
    broker_order_id=None,
    ticker=None,
    side=None,
    order_type=None,
    submitted_limit_price=None,
    reference_price=None,
    fill_price=None,
    fill_quantity=None,
    broker_status="filled",
    details=None
):
    """
    Record an order fill and calculate slippage.
    """

    initialize_fill_slippage_tables()

    ticker = str(ticker or "").upper().strip()
    side = str(side or "").upper().strip()
    order_type = str(order_type or "").upper().strip()

    submitted_limit_price = safe_float(submitted_limit_price)
    reference_price = safe_float(reference_price)
    fill_price = safe_float(fill_price)
    fill_quantity = safe_float(fill_quantity, 0.0)

    fill_value = None

    if fill_price is not None and fill_quantity is not None:
        fill_value = fill_price * fill_quantity

    slippage = calculate_slippage(
        side=side,
        reference_price=reference_price,
        fill_price=fill_price
    )

    fill_payload = {
        "order_key": order_key,
        "broker_order_id": broker_order_id,
        "ticker": ticker,
        "side": side,
        "order_type": order_type,
        "submitted_limit_price": submitted_limit_price,
        "reference_price": reference_price,
        "fill_price": fill_price,
        "fill_quantity": fill_quantity,
        "fill_value": fill_value,
        "broker_status": broker_status,
        "slippage": slippage,
        "details": details or {},
    }

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO order_fills (
            created_at,
            order_key,
            broker_order_id,
            ticker,
            side,
            order_type,
            submitted_limit_price,
            reference_price,
            fill_price,
            fill_quantity,
            fill_value,
            slippage_amount,
            slippage_pct,
            slippage_status,
            broker_status,
            raw_fill_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            order_key,
            broker_order_id,
            ticker,
            side,
            order_type,
            submitted_limit_price,
            reference_price,
            fill_price,
            fill_quantity,
            fill_value,
            slippage.get("slippage_amount"),
            slippage.get("slippage_pct"),
            slippage.get("slippage_status"),
            broker_status,
            safe_json(fill_payload),
        )
    )

    fill_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "fill_id": fill_id,
        "recorded": True,
        "fill": fill_payload,
        "slippage": slippage,
    }


def record_fill_from_broker_response(
    broker_response,
    order_key=None,
    reference_price=None,
    submitted_limit_price=None
):
    """
    Record fill using a broker response dictionary.

    This is flexible because paper/IBKR responses can have different key names.
    """

    if not isinstance(broker_response, dict):
        raise ValueError("broker_response must be a dictionary.")

    ticker = broker_response.get("ticker") or broker_response.get("symbol")
    side = broker_response.get("side")
    order_type = broker_response.get("order_type")

    broker_order_id = (
        broker_response.get("order_id")
        or broker_response.get("broker_order_id")
        or broker_response.get("permId")
    )

    fill_price = (
        broker_response.get("fill_price")
        or broker_response.get("avg_fill_price")
        or broker_response.get("average_fill_price")
        or broker_response.get("avgFillPrice")
        or broker_response.get("filled_avg_price")
    )

    fill_quantity = (
        broker_response.get("filled_quantity")
        or broker_response.get("fill_quantity")
        or broker_response.get("filled")
        or broker_response.get("quantity")
    )

    broker_status = (
        broker_response.get("order_status")
        or broker_response.get("broker_status")
        or "unknown"
    )

    if submitted_limit_price is None:
        submitted_limit_price = broker_response.get("limit_price")

    if reference_price is None:
        reference_price = (
            broker_response.get("reference_price")
            or broker_response.get("latest_price")
            or broker_response.get("market_price")
            or submitted_limit_price
        )

    return record_order_fill(
        order_key=order_key,
        broker_order_id=broker_order_id,
        ticker=ticker,
        side=side,
        order_type=order_type,
        submitted_limit_price=submitted_limit_price,
        reference_price=reference_price,
        fill_price=fill_price,
        fill_quantity=fill_quantity,
        broker_status=broker_status,
        details=broker_response
    )


def read_order_fills(limit=100):
    """
    Read recent fill records.
    """

    initialize_fill_slippage_tables()

    conn = get_database_connection()

    query = """
        SELECT *
        FROM order_fills
        ORDER BY id DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=(int(limit),))
    conn.close()

    return df


def summarize_slippage(ticker=None, side=None, limit=1000):
    """
    Summarize slippage records.
    """

    df = read_order_fills(limit=limit)

    if df.empty:
        return {
            "has_data": False,
            "fill_count": 0,
            "message": "No fill records found.",
        }

    if ticker:
        df = df[df["ticker"].astype(str).str.upper() == str(ticker).upper().strip()]

    if side:
        df = df[df["side"].astype(str).str.upper() == str(side).upper().strip()]

    if df.empty:
        return {
            "has_data": False,
            "fill_count": 0,
            "message": "No fill records found for selected filter.",
        }

    numeric_slippage = pd.to_numeric(df["slippage_pct"], errors="coerce").dropna()
    numeric_quantity = pd.to_numeric(df["fill_quantity"], errors="coerce").fillna(0)
    numeric_fill_price = pd.to_numeric(df["fill_price"], errors="coerce").dropna()

    summary = {
        "has_data": True,
        "fill_count": int(len(df)),
        "total_fill_quantity": float(numeric_quantity.sum()),
        "average_fill_price": float(numeric_fill_price.mean()) if not numeric_fill_price.empty else None,
        "average_slippage_pct": float(numeric_slippage.mean()) if not numeric_slippage.empty else None,
        "worst_slippage_pct": float(numeric_slippage.max()) if not numeric_slippage.empty else None,
        "best_slippage_pct": float(numeric_slippage.min()) if not numeric_slippage.empty else None,
        "ticker_filter": ticker,
        "side_filter": side,
    }

    return summary


def get_fill_slippage_status():
    """
    Return fill/slippage tracker status.
    """

    initialize_fill_slippage_tables()

    df = read_order_fills(limit=100000)
    summary = summarize_slippage(limit=100000)

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fill_count": len(df),
        "summary": summary,
        "purpose": "Track fill prices and slippage against reference prices.",
    }
