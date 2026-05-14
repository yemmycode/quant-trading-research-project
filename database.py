
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd


PROJECT_PATH = Path(r"C:\Users\yemi\OneDrive\Desktop\quant_trading_project")
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


def read_table(table_name, limit=100):
    """
    Read latest rows from a database table.
    """

    initialize_database()

    conn = get_connection()
    query = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {int(limit)}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df
