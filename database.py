
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd


PROJECT_PATH = Path(__file__).resolve().parent
DATA_PATH = PROJECT_PATH / "data"
DATA_PATH.mkdir(parents=True, exist_ok=True)

DATABASE_FILE = DATA_PATH / "quant_trading.db"


def get_connection():
    """
    Create a SQLite database connection.
    """
    return sqlite3.connect(DATABASE_FILE)


def initialize_database():
    """
    Create required database tables if they do not already exist.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_trading_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generated_at TEXT,
            ticker TEXT,
            strategy_type TEXT,
            strategy_label TEXT,
            latest_data_date TEXT,
            latest_close REAL,
            latest_signal INTEGER,
            latest_position INTEGER,
            recommendation TEXT,
            risk_approved INTEGER,
            risk_reason TEXT,
            initial_capital REAL,
            position_size REAL,
            trading_cost REAL,
            paper_portfolio_value REAL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ticker TEXT,
            side TEXT,
            requested_position_size REAL,
            quantity REAL,
            estimated_price REAL,
            estimated_capital REAL,
            status TEXT,
            reason TEXT,
            live_order INTEGER,
            account_equity REAL,
            order_id TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT,
            strategy_type TEXT,
            ticker TEXT,
            short_window REAL,
            long_window REAL,
            rsi_window REAL,
            oversold_level REAL,
            overbought_level REAL,
            regime_window REAL,
            position_size REAL,
            trading_cost REAL,
            total_return_pct REAL,
            annual_return_pct REAL,
            volatility_pct REAL,
            sharpe_ratio REAL,
            sortino_ratio REAL,
            calmar_ratio REAL,
            max_drawdown_pct REAL,
            win_rate_pct REAL,
            average_win_pct REAL,
            average_loss_pct REAL,
            profit_factor REAL,
            recovery_factor REAL,
            final_value REAL,
            buy_trades REAL,
            sell_trades REAL,
            run_id TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

    return DATABASE_FILE


def insert_dataframe(table_name, dataframe):
    """
    Insert a pandas DataFrame into a database table.
    The DataFrame columns should match the table-compatible transformed names.
    """

    if dataframe is None or dataframe.empty:
        return 0

    conn = get_connection()
    dataframe.to_sql(table_name, conn, if_exists="append", index=False)
    inserted_rows = len(dataframe)
    conn.close()

    return inserted_rows


def normalize_paper_status_for_db(status_df):
    """
    Convert paper trading status DataFrame into database-ready format.
    """

    df = status_df.copy()

    column_map = {
        "Generated At": "generated_at",
        "Ticker": "ticker",
        "Strategy Type": "strategy_type",
        "Strategy Label": "strategy_label",
        "Latest Data Date": "latest_data_date",
        "Latest Close": "latest_close",
        "Latest Signal": "latest_signal",
        "Latest Position": "latest_position",
        "Recommendation": "recommendation",
        "Risk Approved": "risk_approved",
        "Risk Reason": "risk_reason",
        "Initial Capital": "initial_capital",
        "Position Size": "position_size",
        "Trading Cost": "trading_cost",
        "Paper Portfolio Value": "paper_portfolio_value"
    }

    df = df.rename(columns=column_map)

    expected_columns = list(column_map.values())

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df = df[expected_columns]
    df["risk_approved"] = df["risk_approved"].astype(int)
    df["latest_data_date"] = df["latest_data_date"].astype(str)
    df["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df


def normalize_order_log_for_db(order_df):
    """
    Convert order log DataFrame into database-ready format.
    """

    df = order_df.copy()

    column_map = {
        "Timestamp": "timestamp",
        "Ticker": "ticker",
        "Side": "side",
        "Requested Position Size": "requested_position_size",
        "Quantity": "quantity",
        "Estimated Price": "estimated_price",
        "Estimated Capital": "estimated_capital",
        "Status": "status",
        "Reason": "reason",
        "Live Order": "live_order",
        "Account Equity": "account_equity",
        "Order ID": "order_id"
    }

    df = df.rename(columns=column_map)

    expected_columns = list(column_map.values())

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df = df[expected_columns]
    df["live_order"] = df["live_order"].astype(int)
    df["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df


def normalize_strategy_results_for_db(results_df, run_id=None):
    """
    Convert strategy results DataFrame into database-ready format.
    """

    df = results_df.copy()

    column_map = {
        "Strategy": "strategy",
        "Strategy Type": "strategy_type",
        "Ticker": "ticker",
        "Short Window": "short_window",
        "Long Window": "long_window",
        "RSI Window": "rsi_window",
        "Oversold Level": "oversold_level",
        "Overbought Level": "overbought_level",
        "Regime Window": "regime_window",
        "Position Size": "position_size",
        "Trading Cost": "trading_cost",
        "Total Return (%)": "total_return_pct",
        "Annual Return (%)": "annual_return_pct",
        "Volatility (%)": "volatility_pct",
        "Sharpe Ratio": "sharpe_ratio",
        "Sortino Ratio": "sortino_ratio",
        "Calmar Ratio": "calmar_ratio",
        "Max Drawdown (%)": "max_drawdown_pct",
        "Win Rate (%)": "win_rate_pct",
        "Average Win (%)": "average_win_pct",
        "Average Loss (%)": "average_loss_pct",
        "Profit Factor": "profit_factor",
        "Recovery Factor": "recovery_factor",
        "Final Value (R)": "final_value",
        "Buy Trades": "buy_trades",
        "Sell Trades": "sell_trades"
    }

    df = df.rename(columns=column_map)

    expected_columns = list(column_map.values())

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    df = df[expected_columns]
    df["run_id"] = run_id
    df["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return df


def save_paper_status(status_df):
    """
    Save paper trading status to SQLite.
    """

    initialize_database()
    db_df = normalize_paper_status_for_db(status_df)
    return insert_dataframe("paper_trading_history", db_df)


def save_order_log(order_df):
    """
    Save order log rows to SQLite.
    """

    initialize_database()
    db_df = normalize_order_log_for_db(order_df)
    return insert_dataframe("order_log", db_df)


def save_strategy_results(results_df, run_id=None):
    """
    Save batch strategy results to SQLite.
    """

    initialize_database()
    db_df = normalize_strategy_results_for_db(results_df, run_id=run_id)
    return insert_dataframe("strategy_results", db_df)



def table_exists(table_name):
    """
    Check whether a table exists in the SQLite database.
    """

    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def read_table(table_name, limit=100):
    """
    Safely read latest rows from a database table.

    If the database or table does not exist yet, return an empty DataFrame.
    """

    initialize_database()

    allowed_tables = [
        "paper_trading_history",
        "order_log",
        "strategy_results",
        "paper_broker_account",
        "paper_broker_positions",
        "paper_broker_orders"
    ]

    if table_name not in allowed_tables:
        raise ValueError(f"Table '{table_name}' is not allowed.")

    if not table_exists(table_name):
        return pd.DataFrame()

    conn = get_connection()

    try:
        query = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT ?"
        df = pd.read_sql_query(query, conn, params=(int(limit),))
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()

    return df


def get_database_status():
    """
    Return simple database status information.
    """

    initialize_database()

    status = {
        "database_file": str(DATABASE_FILE),
        "database_exists": DATABASE_FILE.exists(),
        "tables": {}
    }

    for table_name in [
        "paper_trading_history",
        "order_log",
        "strategy_results"
    ]:
        try:
            df = read_table(table_name, limit=1)
            status["tables"][table_name] = {
                "exists": table_exists(table_name),
                "has_records": not df.empty
            }
        except Exception:
            status["tables"][table_name] = {
                "exists": False,
                "has_records": False
            }

    return status


# ==============================
# Paper Broker State Storage
# ==============================

def initialize_paper_broker_tables():
    """
    Create paper broker state tables if they do not already exist.
    """

    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_broker_account (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            initial_cash REAL,
            cash REAL,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_broker_positions (
            ticker TEXT PRIMARY KEY,
            quantity REAL,
            average_price REAL,
            cost_basis REAL,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_broker_orders (
            order_id TEXT PRIMARY KEY,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            order_type TEXT,
            price REAL,
            order_value REAL,
            status TEXT,
            reason TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_paper_broker_state(initial_cash, cash, positions, orders):
    """
    Save the current PaperBroker account, positions, and orders to SQLite.
    """

    from datetime import datetime

    initialize_paper_broker_tables()

    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()

    # Save account state
    cursor.execute("""
        INSERT OR REPLACE INTO paper_broker_account
        (id, initial_cash, cash, updated_at)
        VALUES (1, ?, ?, ?)
    """, (float(initial_cash), float(cash), updated_at))

    # Replace positions snapshot
    cursor.execute("DELETE FROM paper_broker_positions")

    for ticker, position in positions.items():
        cursor.execute("""
            INSERT OR REPLACE INTO paper_broker_positions
            (ticker, quantity, average_price, cost_basis, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ticker,
            float(position.get("quantity", 0)),
            float(position.get("average_price", 0)),
            float(position.get("cost_basis", 0)),
            updated_at
        ))

    # Save orders
    for order_id, order in orders.items():
        cursor.execute("""
            INSERT OR REPLACE INTO paper_broker_orders
            (order_id, ticker, side, quantity, order_type, price, order_value, status, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(order_id),
            order.get("ticker"),
            order.get("side"),
            float(order.get("quantity", 0)),
            order.get("order_type"),
            float(order.get("price", 0)),
            float(order.get("order_value", 0)),
            order.get("status"),
            order.get("reason", ""),
            order.get("created_at", updated_at)
        ))

    conn.commit()
    conn.close()


def load_paper_broker_state(default_initial_cash=10000):
    """
    Load PaperBroker account, positions, and orders from SQLite.

    If no saved state exists, return default starting state.
    """

    initialize_paper_broker_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT initial_cash, cash
        FROM paper_broker_account
        WHERE id = 1
    """)

    account_row = cursor.fetchone()

    if account_row is None:
        initial_cash = float(default_initial_cash)
        cash = float(default_initial_cash)
    else:
        initial_cash = float(account_row[0])
        cash = float(account_row[1])

    positions_df = pd.read_sql_query(
        "SELECT ticker, quantity, average_price, cost_basis FROM paper_broker_positions",
        conn
    )

    orders_df = pd.read_sql_query(
        "SELECT * FROM paper_broker_orders",
        conn
    )

    conn.close()

    positions = {}

    for _, row in positions_df.iterrows():
        positions[row["ticker"]] = {
            "quantity": float(row["quantity"]),
            "average_price": float(row["average_price"]),
            "cost_basis": float(row["cost_basis"])
        }

    orders = {}

    for _, row in orders_df.iterrows():
        orders[row["order_id"]] = {
            "order_id": row["order_id"],
            "ticker": row["ticker"],
            "side": row["side"],
            "quantity": float(row["quantity"]),
            "order_type": row["order_type"],
            "price": float(row["price"]),
            "order_value": float(row["order_value"]),
            "status": row["status"],
            "reason": row["reason"],
            "created_at": row["created_at"]
        }

    return {
        "initial_cash": initial_cash,
        "cash": cash,
        "positions": positions,
        "orders": orders
    }


def reset_paper_broker_state(initial_cash=10000):
    """
    Reset saved PaperBroker state in SQLite.
    """

    initialize_paper_broker_tables()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM paper_broker_account")
    cursor.execute("DELETE FROM paper_broker_positions")
    cursor.execute("DELETE FROM paper_broker_orders")

    conn.commit()
    conn.close()

    save_paper_broker_state(
        initial_cash=initial_cash,
        cash=initial_cash,
        positions={},
        orders={}
    )
