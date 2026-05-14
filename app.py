
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

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

if str(STRATEGIES_PATH) not in sys.path:
    sys.path.append(str(STRATEGIES_PATH))


from moving_average_strategy import run_backtest
from rsi_strategy import run_rsi_backtest

from paper_trading import run_paper_trading_check


# ==============================
# Page Setup
# ==============================

st.set_page_config(
    page_title="Quant Trading Research Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("Quant Trading Research Dashboard")
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
