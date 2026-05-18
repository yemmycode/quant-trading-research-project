
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ==============================
# Project Paths
# ==============================

PROJECT_PATH = Path(__file__).resolve().parent
STRATEGIES_PATH = PROJECT_PATH / "strategies"
BROKERS_PATH = PROJECT_PATH / "brokers"

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(STRATEGIES_PATH) not in sys.path:
    sys.path.append(str(STRATEGIES_PATH))

if str(BROKERS_PATH) not in sys.path:
    sys.path.append(str(BROKERS_PATH))


from moving_average_strategy import run_backtest
from rsi_strategy import run_rsi_backtest

from paper_trading import run_paper_trading_check

from paper_broker import PaperBroker
from risk_manager import create_risk_manager_from_config
from order_manager import OrderManager
from database import read_table, get_database_status
from config import DASHBOARD_PASSWORD


# ==============================
# Page Setup
# ==============================

st.set_page_config(
    page_title="Quant Trading Research Dashboard",
    page_icon="📈",
    layout="wide"
)



# ==============================
# Secrets Helper
# ==============================

def get_dashboard_password():
    """
    Get dashboard password from Streamlit secrets first,
    then environment/config fallback.
    """

    try:
        if "DASHBOARD_PASSWORD" in st.secrets:
            return st.secrets["DASHBOARD_PASSWORD"]
    except Exception:
        pass

    return DASHBOARD_PASSWORD


# ==============================
# Simple Dashboard Authentication
# ==============================

def check_dashboard_password():
    """
    Simple password gate for demo/private dashboard use.
    """

    if "dashboard_authenticated" not in st.session_state:
        st.session_state.dashboard_authenticated = False

    if st.session_state.dashboard_authenticated:
        return True

    st.title("Quant Trading Research Dashboard Login")
    st.write("Enter the dashboard password to continue.")

    password_input = st.text_input(
        "Password",
        type="password"
    )

    login_button = st.button("Login")

    if login_button:
        if password_input.strip() == get_dashboard_password().strip():
            st.session_state.dashboard_authenticated = True
            st.success("Login successful. Reloading dashboard...")
            st.rerun()
        else:
            st.error("Incorrect password.")

    return False


if not check_dashboard_password():
    st.stop()


logout_col1, logout_col2 = st.columns([5, 1])

with logout_col1:
    st.title("Quant Trading Research Dashboard")

with logout_col2:
    if st.button("Logout"):
        st.session_state.dashboard_authenticated = False
        st.rerun()
st.write(
    "Interactive dashboard for testing moving-average and RSI-based quant strategies."
)

st.warning(
    "Educational research only. Backtested results do not guarantee future performance."
)


# ==============================
# Sidebar Controls
# ==============================

st.sidebar.header("Backtest Settings")

strategy_type = st.sidebar.selectbox(
    "Select Strategy",
    ["Moving Average", "RSI"]
)

ticker = st.sidebar.text_input(
    "Ticker",
    value="SPY"
).upper()

start_date = st.sidebar.text_input(
    "Start Date",
    value="2018-01-01"
)

end_date = st.sidebar.text_input(
    "End Date",
    value="2025-01-01"
)

initial_capital = st.sidebar.number_input(
    "Initial Capital",
    min_value=1000,
    max_value=10000000,
    value=10000,
    step=1000
)

position_size = st.sidebar.slider(
    "Position Size",
    min_value=0.10,
    max_value=1.00,
    value=0.50,
    step=0.05
)

trading_cost = st.sidebar.number_input(
    "Trading Cost per Trade",
    min_value=0.0,
    max_value=0.05,
    value=0.001,
    step=0.001,
    format="%.4f"
)

regime_window = st.sidebar.number_input(
    "Regime Window",
    min_value=50,
    max_value=300,
    value=200,
    step=10
)


if strategy_type == "Moving Average":
    st.sidebar.subheader("Moving Average Parameters")

    short_window = st.sidebar.number_input(
        "Short Moving Average Window",
        min_value=5,
        max_value=100,
        value=20,
        step=5
    )

    long_window = st.sidebar.number_input(
        "Long Moving Average Window",
        min_value=20,
        max_value=300,
        value=50,
        step=10
    )

else:
    st.sidebar.subheader("RSI Parameters")

    rsi_window = st.sidebar.number_input(
        "RSI Window",
        min_value=5,
        max_value=50,
        value=14,
        step=1
    )

    oversold_level = st.sidebar.number_input(
        "Oversold Level",
        min_value=5,
        max_value=50,
        value=30,
        step=5
    )

    overbought_level = st.sidebar.number_input(
        "Overbought Level",
        min_value=50,
        max_value=95,
        value=70,
        step=5
    )


run_button = st.sidebar.button("Run Backtest")


# ==============================
# Helper Functions
# ==============================

def plot_equity_curve(data, initial_capital):
    fig, ax = plt.subplots(figsize=(12, 6))

    buy_hold_equity = initial_capital * data["Buy_Hold_Growth"]
    strategy_equity = initial_capital * data["Strategy_Growth"]

    ax.plot(buy_hold_equity, label="Buy and Hold")
    ax.plot(strategy_equity, label="Strategy")

    ax.set_title("Equity Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio Value")
    ax.legend()
    ax.grid(True)

    return fig


def plot_drawdown(data):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(data["Buy_Hold_Drawdown"], label="Buy and Hold Drawdown")
    ax.plot(data["Strategy_Drawdown"], label="Strategy Drawdown")

    ax.set_title("Drawdown Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.legend()
    ax.grid(True)

    return fig


def plot_rsi(data, oversold_level, overbought_level):
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(data["RSI"], label="RSI")
    ax.axhline(oversold_level, linestyle="--", label="Oversold")
    ax.axhline(overbought_level, linestyle="--", label="Overbought")

    ax.set_title("RSI Indicator")
    ax.set_xlabel("Date")
    ax.set_ylabel("RSI")
    ax.legend()
    ax.grid(True)

    return fig


# ==============================
# Run Backtest
# ==============================

if run_button:
    try:
        with st.spinner("Running backtest..."):

            if strategy_type == "Moving Average":
                data, summary, trade_log = run_backtest(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    short_window=int(short_window),
                    long_window=int(long_window),
                    regime_window=int(regime_window),
                    position_size=float(position_size),
                    trading_cost=float(trading_cost),
                    initial_capital=float(initial_capital)
                )

            else:
                data, summary, trade_log = run_rsi_backtest(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    rsi_window=int(rsi_window),
                    oversold_level=int(oversold_level),
                    overbought_level=int(overbought_level),
                    regime_window=int(regime_window),
                    position_size=float(position_size),
                    trading_cost=float(trading_cost),
                    initial_capital=float(initial_capital)
                )

        st.success("Backtest completed successfully.")

        # ==============================
        # Summary Metrics
        # ==============================

        st.subheader("Performance Summary")

        summary_display = summary.copy()

        numeric_columns = summary_display.select_dtypes(include="number").columns
        summary_display[numeric_columns] = summary_display[numeric_columns].round(2)

        st.dataframe(summary_display, use_container_width=True)

        strategy_row = summary_display.iloc[1]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Return", f"{strategy_row['Total Return (%)']:.2f}%")
        col2.metric("Sharpe Ratio", f"{strategy_row['Sharpe Ratio']:.2f}")
        col3.metric("Max Drawdown", f"{strategy_row['Max Drawdown (%)']:.2f}%")
        col4.metric("Final Value", f"R {strategy_row['Final Value (R)']:,.2f}")

        col5, col6, col7, col8 = st.columns(4)

        if "Sortino Ratio" in strategy_row:
            col5.metric("Sortino Ratio", f"{strategy_row['Sortino Ratio']:.2f}")

        if "Calmar Ratio" in strategy_row:
            col6.metric("Calmar Ratio", f"{strategy_row['Calmar Ratio']:.2f}")

        if "Profit Factor" in strategy_row:
            col7.metric("Profit Factor", f"{strategy_row['Profit Factor']:.2f}")

        if "Win Rate (%)" in strategy_row:
            col8.metric("Win Rate", f"{strategy_row['Win Rate (%)']:.2f}%")

        # ==============================
        # Charts
        # ==============================

        st.subheader("Equity Curve")
        st.pyplot(plot_equity_curve(data, initial_capital))

        st.subheader("Drawdown Chart")
        st.pyplot(plot_drawdown(data))

        if strategy_type == "RSI":
            st.subheader("RSI Indicator")
            st.pyplot(plot_rsi(data, oversold_level, overbought_level))

        # ==============================
        # Trade Log
        # ==============================

        st.subheader("Trade Log")

        if trade_log.empty:
            st.info("No completed trades found for this strategy setup.")
        else:
            trade_log_display = trade_log.copy()

            numeric_trade_columns = trade_log_display.select_dtypes(include="number").columns
            trade_log_display[numeric_trade_columns] = trade_log_display[numeric_trade_columns].round(2)

            st.dataframe(trade_log_display, use_container_width=True)

            csv_trade_log = trade_log_display.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Trade Log CSV",
                data=csv_trade_log,
                file_name=f"{ticker}_{strategy_type.lower().replace(' ', '_')}_trade_log.csv",
                mime="text/csv"
            )

        # ==============================
        # Data Preview
        # ==============================

        with st.expander("View Backtest Data"):
            st.dataframe(data.tail(100), use_container_width=True)

    except Exception as e:
        st.error("Backtest failed.")
        st.exception(e)

else:
    st.info("Use the sidebar settings, then click 'Run Backtest'.")


# ==============================
# Paper Trading Mode
# ==============================

st.markdown("---")
st.header("Paper Trading Mode")
st.write(
    "This section checks the latest strategy signal without placing any real trades."
)

paper_col1, paper_col2 = st.columns(2)

with paper_col1:
    paper_strategy = st.selectbox(
        "Paper Trading Strategy",
        ["moving_average", "rsi"]
    )

with paper_col2:
    paper_ticker = st.text_input(
        "Paper Trading Ticker",
        value="SPY"
    ).upper()

run_paper_button = st.button("Run Paper Trading Check")

if run_paper_button:
    try:
        with st.spinner("Running paper trading check..."):
            paper_status, paper_data, paper_summary, paper_trade_log = run_paper_trading_check(
                strategy_type=paper_strategy,
                ticker=paper_ticker
            )

        st.success("Paper trading check completed.")

        st.subheader("Latest Paper Trading Status")
        st.dataframe(paper_status, use_container_width=True)

        latest_status = paper_status.iloc[0]

        pcol1, pcol2, pcol3, pcol4 = st.columns(4)

        pcol1.metric("Latest Close", f"{latest_status['Latest Close']:.2f}")
        pcol2.metric("Latest Signal", int(latest_status["Latest Signal"]))
        pcol3.metric("Latest Position", int(latest_status["Latest Position"]))
        pcol4.metric(
            "Paper Value",
            f"R {latest_status['Paper Portfolio Value']:,.2f}"
        )

        st.info(f"Recommendation: {latest_status['Recommendation']}")

        st.subheader("Paper Trading Equity Curve")
        st.pyplot(plot_equity_curve(paper_data, latest_status["Initial Capital"]))

        st.subheader("Paper Trading Trade Log")
        if paper_trade_log.empty:
            st.info("No completed paper trades found.")
        else:
            st.dataframe(paper_trade_log, use_container_width=True)

    except Exception as e:
        st.error("Paper trading check failed.")
        st.exception(e)


# ==============================
# Paper Trading History
# ==============================

st.markdown("---")
st.header("Paper Trading History")

history_file = PROJECT_PATH / "results" / "paper_trading_history.csv"

if history_file.exists():
    paper_history = pd.read_csv(history_file)
    st.dataframe(paper_history.tail(50), use_container_width=True)

    history_csv = paper_history.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Paper Trading History CSV",
        data=history_csv,
        file_name="paper_trading_history.csv",
        mime="text/csv"
    )
else:
    st.info("No paper trading history found yet. Run a paper trading check first.")




# ==============================
# Emergency Stop Control
# ==============================

st.markdown("---")
st.header("Emergency Stop Control")
st.write(
    "Emergency stop blocks all simulated paper order submissions from the dashboard."
)

if "dashboard_emergency_stop" not in st.session_state:
    st.session_state.dashboard_emergency_stop = False

emergency_stop_value = st.toggle(
    "Activate Emergency Stop",
    value=st.session_state.dashboard_emergency_stop,
    key="emergency_stop_toggle"
)

st.session_state.dashboard_emergency_stop = emergency_stop_value

if st.session_state.dashboard_emergency_stop:
    st.error("EMERGENCY STOP IS ACTIVE: all simulated paper orders are blocked.")
else:
    st.success("Emergency stop is inactive.")


# ==============================
# Manual Confirmation Order Ticket
# ==============================

st.markdown("---")
st.header("Manual Confirmation Order Ticket")
st.write(
    "This section submits simulated orders to the Paper Broker only. "
    "It does not place live trades."
)

if "paper_broker" not in st.session_state:
    st.session_state.paper_broker = PaperBroker(initial_cash=10000)

if "risk_manager" not in st.session_state:
    st.session_state.risk_manager = create_risk_manager_from_config()

if "order_manager" not in st.session_state:
    st.session_state.order_manager = OrderManager(
        broker=st.session_state.paper_broker,
        risk_manager=st.session_state.risk_manager,
        results_path=PROJECT_PATH / "results"
    )

order_col1, order_col2, order_col3 = st.columns(3)

with order_col1:
    order_ticker = st.text_input(
        "Order Ticker",
        value="SPY",
        key="order_ticker_input"
    ).upper()

with order_col2:
    order_side = st.selectbox(
        "Order Side",
        ["buy", "sell"],
        key="order_side_select"
    )

with order_col3:
    order_position_size = st.slider(
        "Order Position Size",
        min_value=0.01,
        max_value=0.25,
        value=0.05,
        step=0.01,
        key="order_position_size_slider"
    )

st.subheader("Paper Broker Account")

account_info = st.session_state.paper_broker.get_account_info()
st.json(account_info)

positions = st.session_state.paper_broker.get_positions()

if positions:
    st.write("Current Paper Positions")
    st.dataframe(pd.DataFrame(positions), use_container_width=True)
else:
    st.info("No current paper positions.")

st.subheader("Order Preview")

try:
    latest_price = st.session_state.paper_broker.get_latest_price(order_ticker)
    account_equity = account_info["equity"]
    estimated_capital = account_equity * order_position_size
    estimated_quantity = int(estimated_capital // latest_price)

    preview_data = {
        "Ticker": order_ticker,
        "Side": order_side,
        "Latest Price": round(latest_price, 2),
        "Account Equity": round(account_equity, 2),
        "Requested Position Size": f"{order_position_size:.2%}",
        "Estimated Capital": round(estimated_capital, 2),
        "Estimated Quantity": estimated_quantity,
        "Broker Mode": "Paper Broker Only"
    }

    st.json(preview_data)

except Exception as e:
    st.error("Could not generate order preview.")
    st.exception(e)
    estimated_quantity = 0

manual_confirmation = st.checkbox(
    "I confirm this simulated paper order ticket.",
    key="manual_order_confirmation"
)

submit_order_button = st.button("Submit Simulated Paper Order")

if submit_order_button:
    try:
        if st.session_state.get("dashboard_emergency_stop", False):
            st.error("Order blocked: dashboard emergency stop is active.")
            st.stop()

        result = st.session_state.order_manager.submit_managed_order(
            ticker=order_ticker,
            side=order_side,
            proposed_position_size=order_position_size,
            current_daily_loss=0.00,
            current_weekly_loss=0.00,
            current_total_drawdown=0.00,
            manual_confirmation_given=manual_confirmation,
            live_order=False
        )

        if result["approved"] and result["status"] == "filled":
            st.success("Simulated paper order filled.")
        elif result["approved"]:
            st.warning(f"Order approved but status is: {result['status']}")
        else:
            st.error("Order blocked by risk manager.")

        st.write("Order Result")
        st.json(result)

    except Exception as e:
        st.error("Order submission failed.")
        st.exception(e)

st.subheader("Recent Order Log")

order_log_file = PROJECT_PATH / "results" / "order_log.csv"

if order_log_file.exists():
    order_log = pd.read_csv(order_log_file)
    st.dataframe(order_log.tail(20), use_container_width=True)
else:
    st.info("No order log found yet.")




# ==============================
# Database Viewer
# ==============================

st.markdown("---")
st.header("Database Viewer")
st.write("View latest records stored in the local SQLite database.")

try:
    db_status = get_database_status()

    with st.expander("Database Status"):
        st.json(db_status)

except Exception as e:
    st.warning("Database status could not be loaded yet.")
    st.caption(str(e))

db_table = st.selectbox(
    "Select Database Table",
    ["paper_trading_history", "order_log", "strategy_results"]
)

db_limit = st.number_input(
    "Number of rows to display",
    min_value=10,
    max_value=500,
    value=50,
    step=10
)

try:
    db_data = read_table(db_table, limit=db_limit)

    if db_data.empty:
        st.info(
            "No records found yet for this table. "
            "Run a paper trading check, order ticket test, or research pipeline first."
        )
    else:
        st.dataframe(db_data, use_container_width=True)

        db_csv = db_data.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=f"Download {db_table} CSV",
            data=db_csv,
            file_name=f"{db_table}.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error("Could not read database table.")
    st.exception(e)
