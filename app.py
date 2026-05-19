from safety_manager import read_emergency_stop_state, activate_emergency_stop, deactivate_emergency_stop, is_emergency_stop_active

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
from bollinger_bands_strategy import run_bollinger_backtest
from momentum_strategy import run_momentum_backtest
from breakout_strategy import run_breakout_backtest


from paper_trading import run_paper_trading_check

from paper_broker import PaperBroker
from broker_factory import get_broker, list_available_brokers
from risk_manager import create_risk_manager_from_config
from order_manager import OrderManager
from database import read_table, get_database_status
from report_generator import generate_excel_strategy_report
from config import (
    DASHBOARD_PASSWORD,
    EXECUTION_MODE,
    DEFAULT_BROKER,
    PRIMARY_MARKET,
    DEFAULT_CURRENCY,
    ALLOW_LIVE_TRADING
)


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


st.subheader("System Mode")

mode_col1, mode_col2, mode_col3, mode_col4 = st.columns(4)

mode_col1.metric("Execution Mode", EXECUTION_MODE)
mode_col2.metric("Default Broker", DEFAULT_BROKER)
mode_col3.metric("Primary Market", PRIMARY_MARKET)
mode_col4.metric("Currency", DEFAULT_CURRENCY)

if EXECUTION_MODE == "LIVE_MANUAL" and ALLOW_LIVE_TRADING:
    st.error("LIVE MANUAL MODE IS ENABLED. Real broker orders may be possible if broker integration is active.")
else:
    st.info("Live trading is disabled. The system is operating in research or paper/sandbox-safe mode.")


st.subheader("Broker Readiness")

broker_status_data = pd.DataFrame(list_available_brokers())
st.dataframe(broker_status_data, use_container_width=True)


st.subheader("Persistent Emergency Stop")

emergency_state = read_emergency_stop_state()

if emergency_state.get("active", False):
    st.error(f"EMERGENCY STOP ACTIVE: {emergency_state.get('reason', '')}")
else:
    st.success("Emergency stop is inactive.")

st.json(emergency_state)

stop_col1, stop_col2 = st.columns(2)

with stop_col1:
    emergency_reason = st.text_input(
        "Emergency Stop Reason",
        value="Manual dashboard emergency stop.",
        key="emergency_stop_reason"
    )

    if st.button("Activate Emergency Stop"):
        activate_emergency_stop(
            reason=emergency_reason,
            updated_by="streamlit_dashboard"
        )
        st.rerun()

with stop_col2:
    deactivate_reason = st.text_input(
        "Deactivation Reason",
        value="Manual dashboard deactivation.",
        key="emergency_stop_deactivate_reason"
    )

    if st.button("Deactivate Emergency Stop"):
        deactivate_emergency_stop(
            reason=deactivate_reason,
            updated_by="streamlit_dashboard"
        )
        st.rerun()





# ==============================
# Sidebar Controls
# ==============================

st.sidebar.header("Backtest Settings")

strategy_type = st.sidebar.selectbox(
    "Select Strategy",
    ["Moving Average", "RSI", "Bollinger Bands", "Momentum", "Breakout"]
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

elif strategy_type == "RSI":
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

elif strategy_type == "Bollinger Bands":
    st.sidebar.subheader("Bollinger Bands Parameters")

    bollinger_window = st.sidebar.number_input(
        "Bollinger Window",
        min_value=10,
        max_value=100,
        value=20,
        step=5
    )

    bollinger_std = st.sidebar.number_input(
        "Number of Standard Deviations",
        min_value=1.0,
        max_value=4.0,
        value=2.0,
        step=0.5
    )

elif strategy_type == "Momentum":
    st.sidebar.subheader("Momentum Parameters")

    momentum_window = st.sidebar.number_input(
        "Momentum Window",
        min_value=10,
        max_value=200,
        value=60,
        step=10
    )

elif strategy_type == "Breakout":
    st.sidebar.subheader("Breakout Parameters")

    breakout_window = st.sidebar.number_input(
        "Breakout Window",
        min_value=20,
        max_value=250,
        value=50,
        step=10
    )

    exit_window = st.sidebar.number_input(
        "Exit Window",
        min_value=10,
        max_value=150,
        value=20,
        step=10
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

            elif strategy_type == "RSI":
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

            elif strategy_type == "Bollinger Bands":
                data, summary, trade_log = run_bollinger_backtest(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    window=int(bollinger_window),
                    num_std=float(bollinger_std),
                    regime_window=int(regime_window),
                    position_size=float(position_size),
                    trading_cost=float(trading_cost),
                    initial_capital=float(initial_capital)
                )

            elif strategy_type == "Momentum":
                data, summary, trade_log = run_momentum_backtest(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    momentum_window=int(momentum_window),
                    regime_window=int(regime_window),
                    position_size=float(position_size),
                    trading_cost=float(trading_cost),
                    initial_capital=float(initial_capital)
                )

            elif strategy_type == "Breakout":
                data, summary, trade_log = run_breakout_backtest(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    breakout_window=int(breakout_window),
                    exit_window=int(exit_window),
                    regime_window=int(regime_window),
                    position_size=float(position_size),
                    trading_cost=float(trading_cost),
                    initial_capital=float(initial_capital)
                )

            else:
                raise ValueError(f"Unknown strategy type: {strategy_type}")

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
        # Downloadable Strategy Report
        # ==============================

        st.subheader("Download Strategy Report")

        strategy_settings = {
            "Strategy Type": strategy_type,
            "Ticker": ticker,
            "Start Date": start_date,
            "End Date": end_date,
            "Initial Capital": initial_capital,
            "Position Size": position_size,
            "Trading Cost": trading_cost,
            "Regime Window": regime_window
        }

        if strategy_type == "Moving Average":
            strategy_settings.update({
                "Short Window": short_window,
                "Long Window": long_window
            })

        elif strategy_type == "RSI":
            strategy_settings.update({
                "RSI Window": rsi_window,
                "Oversold Level": oversold_level,
                "Overbought Level": overbought_level
            })

        elif strategy_type == "Bollinger Bands":
            strategy_settings.update({
                "Bollinger Window": bollinger_window,
                "Bollinger Std": bollinger_std
            })

        elif strategy_type == "Momentum":
            strategy_settings.update({
                "Momentum Window": momentum_window
            })

        elif strategy_type == "Breakout":
            strategy_settings.update({
                "Breakout Window": breakout_window,
                "Exit Window": exit_window
            })

        excel_report = generate_excel_strategy_report(
            summary=summary,
            data=data,
            trade_log=trade_log,
            strategy_settings=strategy_settings
        )

        report_file_name = f"{ticker}_{strategy_type.lower().replace(' ', '_')}_strategy_report.xlsx"

        st.download_button(
            label="Download Excel Strategy Report",
            data=excel_report,
            file_name=report_file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
# Strategy Comparison Dashboard
# ==============================

st.markdown("---")
st.header("Strategy Comparison Dashboard")
st.write(
    "Compare multiple strategies on the same ticker, date range, capital, "
    "position size, trading cost, and regime filter."
)

comparison_col1, comparison_col2, comparison_col3 = st.columns(3)

with comparison_col1:
    comparison_ticker = st.text_input(
        "Comparison Ticker",
        value="SPY",
        key="comparison_ticker"
    ).upper()

with comparison_col2:
    comparison_start_date = st.text_input(
        "Comparison Start Date",
        value="2018-01-01",
        key="comparison_start_date"
    )

with comparison_col3:
    comparison_end_date = st.text_input(
        "Comparison End Date",
        value="2025-01-01",
        key="comparison_end_date"
    )

comparison_col4, comparison_col5, comparison_col6 = st.columns(3)

with comparison_col4:
    comparison_initial_capital = st.number_input(
        "Comparison Initial Capital",
        min_value=1000,
        max_value=10000000,
        value=10000,
        step=1000,
        key="comparison_initial_capital"
    )

with comparison_col5:
    comparison_position_size = st.slider(
        "Comparison Position Size",
        min_value=0.10,
        max_value=1.00,
        value=0.50,
        step=0.05,
        key="comparison_position_size"
    )

with comparison_col6:
    comparison_trading_cost = st.number_input(
        "Comparison Trading Cost",
        min_value=0.0,
        max_value=0.05,
        value=0.001,
        step=0.001,
        format="%.4f",
        key="comparison_trading_cost"
    )

comparison_regime_window = st.number_input(
    "Comparison Regime Window",
    min_value=50,
    max_value=300,
    value=200,
    step=10,
    key="comparison_regime_window"
)

selected_comparison_strategies = st.multiselect(
    "Select Strategies to Compare",
    [
        "Moving Average",
        "RSI",
        "Bollinger Bands",
        "Momentum",
        "Breakout"
    ],
    default=[
        "Moving Average",
        "RSI",
        "Bollinger Bands",
        "Momentum",
        "Breakout"
    ]
)

run_comparison_button = st.button("Run Strategy Comparison")

if run_comparison_button:
    if not selected_comparison_strategies:
        st.warning("Please select at least one strategy to compare.")
    else:
        comparison_results = []
        comparison_data = {}

        with st.spinner("Running strategy comparison..."):

            for selected_strategy in selected_comparison_strategies:
                try:
                    if selected_strategy == "Moving Average":
                        comparison_result_data, comparison_summary, comparison_trade_log = run_backtest(
                            ticker=comparison_ticker,
                            start_date=comparison_start_date,
                            end_date=comparison_end_date,
                            short_window=20,
                            long_window=50,
                            regime_window=int(comparison_regime_window),
                            position_size=float(comparison_position_size),
                            trading_cost=float(comparison_trading_cost),
                            initial_capital=float(comparison_initial_capital)
                        )

                        strategy_row = comparison_summary[
                            comparison_summary["Strategy"] == "Quant Strategy"
                        ].copy()

                        strategy_label = "Moving Average 20/50"

                    elif selected_strategy == "RSI":
                        comparison_result_data, comparison_summary, comparison_trade_log = run_rsi_backtest(
                            ticker=comparison_ticker,
                            start_date=comparison_start_date,
                            end_date=comparison_end_date,
                            rsi_window=14,
                            oversold_level=30,
                            overbought_level=70,
                            regime_window=int(comparison_regime_window),
                            position_size=float(comparison_position_size),
                            trading_cost=float(comparison_trading_cost),
                            initial_capital=float(comparison_initial_capital)
                        )

                        strategy_row = comparison_summary[
                            comparison_summary["Strategy"] == "RSI Strategy"
                        ].copy()

                        strategy_label = "RSI 14 / 30-70"

                    elif selected_strategy == "Bollinger Bands":
                        comparison_result_data, comparison_summary, comparison_trade_log = run_bollinger_backtest(
                            ticker=comparison_ticker,
                            start_date=comparison_start_date,
                            end_date=comparison_end_date,
                            window=20,
                            num_std=2,
                            regime_window=int(comparison_regime_window),
                            position_size=float(comparison_position_size),
                            trading_cost=float(comparison_trading_cost),
                            initial_capital=float(comparison_initial_capital)
                        )

                        strategy_row = comparison_summary[
                            comparison_summary["Strategy"] == "Bollinger Bands Strategy"
                        ].copy()

                        strategy_label = "Bollinger Bands 20 / 2 std"

                    elif selected_strategy == "Momentum":
                        comparison_result_data, comparison_summary, comparison_trade_log = run_momentum_backtest(
                            ticker=comparison_ticker,
                            start_date=comparison_start_date,
                            end_date=comparison_end_date,
                            momentum_window=60,
                            regime_window=int(comparison_regime_window),
                            position_size=float(comparison_position_size),
                            trading_cost=float(comparison_trading_cost),
                            initial_capital=float(comparison_initial_capital)
                        )

                        strategy_row = comparison_summary[
                            comparison_summary["Strategy"] == "Momentum Strategy"
                        ].copy()

                        strategy_label = "Momentum 60"

                    elif selected_strategy == "Breakout":
                        comparison_result_data, comparison_summary, comparison_trade_log = run_breakout_backtest(
                            ticker=comparison_ticker,
                            start_date=comparison_start_date,
                            end_date=comparison_end_date,
                            breakout_window=50,
                            exit_window=20,
                            regime_window=int(comparison_regime_window),
                            position_size=float(comparison_position_size),
                            trading_cost=float(comparison_trading_cost),
                            initial_capital=float(comparison_initial_capital)
                        )

                        strategy_row = comparison_summary[
                            comparison_summary["Strategy"] == "Breakout Strategy"
                        ].copy()

                        strategy_label = "Breakout 50 / Exit 20"

                    else:
                        continue

                    if not strategy_row.empty:
                        strategy_row["Comparison Label"] = strategy_label
                        comparison_results.append(strategy_row)

                        comparison_data[strategy_label] = comparison_result_data

                except Exception as e:
                    st.warning(f"{selected_strategy} failed: {e}")

        if not comparison_results:
            st.error("No strategy comparison results were generated.")
        else:
            comparison_table = pd.concat(comparison_results, ignore_index=True)

            numeric_columns = comparison_table.select_dtypes(include="number").columns
            comparison_table[numeric_columns] = comparison_table[numeric_columns].round(2)

            st.subheader("Strategy Comparison Table")

            key_columns = [
                "Comparison Label",
                "Strategy",
                "Ticker",
                "Total Return (%)",
                "Annual Return (%)",
                "Volatility (%)",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Calmar Ratio",
                "Max Drawdown (%)",
                "Win Rate (%)",
                "Profit Factor",
                "Recovery Factor",
                "Final Value (R)",
                "Buy Trades",
                "Sell Trades"
            ]

            existing_key_columns = [
                col for col in key_columns if col in comparison_table.columns
            ]

            comparison_table_display = comparison_table[existing_key_columns].sort_values(
                by="Sharpe Ratio",
                ascending=False
            )

            st.dataframe(comparison_table_display, use_container_width=True)

            st.subheader("Strategy Ranking")

            best_strategy = comparison_table_display.iloc[0]

            rank_col1, rank_col2, rank_col3, rank_col4 = st.columns(4)

            rank_col1.metric(
                "Best Strategy",
                best_strategy["Comparison Label"]
            )

            rank_col2.metric(
                "Best Sharpe",
                f"{best_strategy['Sharpe Ratio']:.2f}"
            )

            rank_col3.metric(
                "Best Return",
                f"{best_strategy['Total Return (%)']:.2f}%"
            )

            rank_col4.metric(
                "Max Drawdown",
                f"{best_strategy['Max Drawdown (%)']:.2f}%"
            )

            st.subheader("Equity Curve Comparison")

            fig, ax = plt.subplots(figsize=(12, 6))

            for label, strategy_data in comparison_data.items():
                equity_curve = comparison_initial_capital * strategy_data["Strategy_Growth"]
                ax.plot(equity_curve, label=label)

            ax.set_title(f"Strategy Equity Curve Comparison - {comparison_ticker}")
            ax.set_xlabel("Date")
            ax.set_ylabel("Portfolio Value")
            ax.legend()
            ax.grid(True)

            st.pyplot(fig)

            st.subheader("Drawdown Comparison")

            fig_drawdown, ax_drawdown = plt.subplots(figsize=(12, 6))

            for label, strategy_data in comparison_data.items():
                ax_drawdown.plot(
                    strategy_data["Strategy_Drawdown"],
                    label=label
                )

            ax_drawdown.set_title(f"Strategy Drawdown Comparison - {comparison_ticker}")
            ax_drawdown.set_xlabel("Date")
            ax_drawdown.set_ylabel("Drawdown")
            ax_drawdown.legend()
            ax_drawdown.grid(True)

            st.pyplot(fig_drawdown)

            comparison_csv = comparison_table_display.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Strategy Comparison CSV",
                data=comparison_csv,
                file_name=f"{comparison_ticker}_strategy_comparison.csv",
                mime="text/csv"
            )




# ==============================
# Parameter Optimization Dashboard
# ==============================

st.markdown("---")
st.header("Parameter Optimization Dashboard")
st.write(
    "Test multiple parameter presets across strategies and rank the best-performing setups."
)

opt_col1, opt_col2, opt_col3 = st.columns(3)

with opt_col1:
    opt_ticker = st.text_input(
        "Optimization Ticker",
        value="SPY",
        key="opt_ticker"
    ).upper()

with opt_col2:
    opt_start_date = st.text_input(
        "Optimization Start Date",
        value="2018-01-01",
        key="opt_start_date"
    )

with opt_col3:
    opt_end_date = st.text_input(
        "Optimization End Date",
        value="2025-01-01",
        key="opt_end_date"
    )

opt_col4, opt_col5, opt_col6 = st.columns(3)

with opt_col4:
    opt_initial_capital = st.number_input(
        "Optimization Initial Capital",
        min_value=1000,
        max_value=10000000,
        value=10000,
        step=1000,
        key="opt_initial_capital"
    )

with opt_col5:
    opt_position_size = st.slider(
        "Optimization Position Size",
        min_value=0.10,
        max_value=1.00,
        value=0.50,
        step=0.05,
        key="opt_position_size"
    )

with opt_col6:
    opt_trading_cost = st.number_input(
        "Optimization Trading Cost",
        min_value=0.0,
        max_value=0.05,
        value=0.001,
        step=0.001,
        format="%.4f",
        key="opt_trading_cost"
    )

opt_regime_window = st.number_input(
    "Optimization Regime Window",
    min_value=50,
    max_value=300,
    value=200,
    step=10,
    key="opt_regime_window"
)

opt_metric = st.selectbox(
    "Rank Results By",
    [
        "Sharpe Ratio",
        "Sortino Ratio",
        "Calmar Ratio",
        "Total Return (%)",
        "Annual Return (%)",
        "Profit Factor",
        "Recovery Factor"
    ],
    key="opt_metric"
)

opt_selected_strategies = st.multiselect(
    "Select Strategies for Optimization",
    [
        "Moving Average",
        "RSI",
        "Bollinger Bands",
        "Momentum",
        "Breakout"
    ],
    default=[
        "Moving Average",
        "RSI",
        "Bollinger Bands",
        "Momentum",
        "Breakout"
    ],
    key="opt_selected_strategies"
)

run_optimization_button = st.button("Run Parameter Optimization")

if run_optimization_button:
    if not opt_selected_strategies:
        st.warning("Please select at least one strategy.")
    else:
        optimization_results = []
        optimization_curves = {}

        moving_average_presets = [
            {"short_window": 10, "long_window": 50},
            {"short_window": 20, "long_window": 50},
            {"short_window": 20, "long_window": 100},
            {"short_window": 50, "long_window": 200},
        ]

        rsi_presets = [
            {"rsi_window": 14, "oversold_level": 30, "overbought_level": 70},
            {"rsi_window": 14, "oversold_level": 35, "overbought_level": 65},
            {"rsi_window": 21, "oversold_level": 30, "overbought_level": 70},
        ]

        bollinger_presets = [
            {"window": 20, "num_std": 2},
            {"window": 20, "num_std": 2.5},
            {"window": 30, "num_std": 2},
        ]

        momentum_presets = [
            {"momentum_window": 30},
            {"momentum_window": 60},
            {"momentum_window": 90},
        ]

        breakout_presets = [
            {"breakout_window": 50, "exit_window": 20},
            {"breakout_window": 100, "exit_window": 30},
            {"breakout_window": 120, "exit_window": 50},
        ]

        with st.spinner("Running parameter optimization..."):

            if "Moving Average" in opt_selected_strategies:
                for preset in moving_average_presets:
                    try:
                        opt_data, opt_summary, opt_trade_log = run_backtest(
                            ticker=opt_ticker,
                            start_date=opt_start_date,
                            end_date=opt_end_date,
                            short_window=preset["short_window"],
                            long_window=preset["long_window"],
                            regime_window=int(opt_regime_window),
                            position_size=float(opt_position_size),
                            trading_cost=float(opt_trading_cost),
                            initial_capital=float(opt_initial_capital)
                        )

                        row = opt_summary[
                            opt_summary["Strategy"] == "Quant Strategy"
                        ].copy()

                        if not row.empty:
                            label = f"MA {preset['short_window']}/{preset['long_window']}"
                            row["Optimization Label"] = label
                            row["Strategy Family"] = "Moving Average"
                            optimization_results.append(row)
                            optimization_curves[label] = opt_data

                    except Exception as e:
                        st.warning(f"Moving Average preset failed: {preset} | {e}")

            if "RSI" in opt_selected_strategies:
                for preset in rsi_presets:
                    try:
                        opt_data, opt_summary, opt_trade_log = run_rsi_backtest(
                            ticker=opt_ticker,
                            start_date=opt_start_date,
                            end_date=opt_end_date,
                            rsi_window=preset["rsi_window"],
                            oversold_level=preset["oversold_level"],
                            overbought_level=preset["overbought_level"],
                            regime_window=int(opt_regime_window),
                            position_size=float(opt_position_size),
                            trading_cost=float(opt_trading_cost),
                            initial_capital=float(opt_initial_capital)
                        )

                        row = opt_summary[
                            opt_summary["Strategy"] == "RSI Strategy"
                        ].copy()

                        if not row.empty:
                            label = (
                                f"RSI {preset['rsi_window']} "
                                f"{preset['oversold_level']}/{preset['overbought_level']}"
                            )
                            row["Optimization Label"] = label
                            row["Strategy Family"] = "RSI"
                            optimization_results.append(row)
                            optimization_curves[label] = opt_data

                    except Exception as e:
                        st.warning(f"RSI preset failed: {preset} | {e}")

            if "Bollinger Bands" in opt_selected_strategies:
                for preset in bollinger_presets:
                    try:
                        opt_data, opt_summary, opt_trade_log = run_bollinger_backtest(
                            ticker=opt_ticker,
                            start_date=opt_start_date,
                            end_date=opt_end_date,
                            window=preset["window"],
                            num_std=preset["num_std"],
                            regime_window=int(opt_regime_window),
                            position_size=float(opt_position_size),
                            trading_cost=float(opt_trading_cost),
                            initial_capital=float(opt_initial_capital)
                        )

                        row = opt_summary[
                            opt_summary["Strategy"] == "Bollinger Bands Strategy"
                        ].copy()

                        if not row.empty:
                            label = f"BB {preset['window']}/{preset['num_std']} std"
                            row["Optimization Label"] = label
                            row["Strategy Family"] = "Bollinger Bands"
                            optimization_results.append(row)
                            optimization_curves[label] = opt_data

                    except Exception as e:
                        st.warning(f"Bollinger preset failed: {preset} | {e}")

            if "Momentum" in opt_selected_strategies:
                for preset in momentum_presets:
                    try:
                        opt_data, opt_summary, opt_trade_log = run_momentum_backtest(
                            ticker=opt_ticker,
                            start_date=opt_start_date,
                            end_date=opt_end_date,
                            momentum_window=preset["momentum_window"],
                            regime_window=int(opt_regime_window),
                            position_size=float(opt_position_size),
                            trading_cost=float(opt_trading_cost),
                            initial_capital=float(opt_initial_capital)
                        )

                        row = opt_summary[
                            opt_summary["Strategy"] == "Momentum Strategy"
                        ].copy()

                        if not row.empty:
                            label = f"Momentum {preset['momentum_window']}"
                            row["Optimization Label"] = label
                            row["Strategy Family"] = "Momentum"
                            optimization_results.append(row)
                            optimization_curves[label] = opt_data

                    except Exception as e:
                        st.warning(f"Momentum preset failed: {preset} | {e}")

            if "Breakout" in opt_selected_strategies:
                for preset in breakout_presets:
                    try:
                        opt_data, opt_summary, opt_trade_log = run_breakout_backtest(
                            ticker=opt_ticker,
                            start_date=opt_start_date,
                            end_date=opt_end_date,
                            breakout_window=preset["breakout_window"],
                            exit_window=preset["exit_window"],
                            regime_window=int(opt_regime_window),
                            position_size=float(opt_position_size),
                            trading_cost=float(opt_trading_cost),
                            initial_capital=float(opt_initial_capital)
                        )

                        row = opt_summary[
                            opt_summary["Strategy"] == "Breakout Strategy"
                        ].copy()

                        if not row.empty:
                            label = (
                                f"Breakout {preset['breakout_window']}/"
                                f"{preset['exit_window']}"
                            )
                            row["Optimization Label"] = label
                            row["Strategy Family"] = "Breakout"
                            optimization_results.append(row)
                            optimization_curves[label] = opt_data

                    except Exception as e:
                        st.warning(f"Breakout preset failed: {preset} | {e}")

        if not optimization_results:
            st.error("No optimization results were generated.")
        else:
            optimization_table = pd.concat(optimization_results, ignore_index=True)

            numeric_columns = optimization_table.select_dtypes(include="number").columns
            optimization_table[numeric_columns] = optimization_table[numeric_columns].round(2)

            if opt_metric not in optimization_table.columns:
                st.warning(f"{opt_metric} not found. Ranking by Sharpe Ratio instead.")
                opt_metric = "Sharpe Ratio"

            optimization_table = optimization_table.sort_values(
                by=opt_metric,
                ascending=False
            )

            st.subheader("Optimization Results")

            display_columns = [
                "Optimization Label",
                "Strategy Family",
                "Strategy",
                "Ticker",
                "Total Return (%)",
                "Annual Return (%)",
                "Volatility (%)",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Calmar Ratio",
                "Max Drawdown (%)",
                "Win Rate (%)",
                "Profit Factor",
                "Recovery Factor",
                "Final Value (R)",
                "Buy Trades",
                "Sell Trades"
            ]

            available_columns = [
                col for col in display_columns if col in optimization_table.columns
            ]

            st.dataframe(
                optimization_table[available_columns],
                use_container_width=True
            )

            st.subheader("Best Parameter Setup")

            best_row = optimization_table.iloc[0]

            best_col1, best_col2, best_col3, best_col4 = st.columns(4)

            best_col1.metric(
                "Best Setup",
                best_row["Optimization Label"]
            )

            best_col2.metric(
                f"Best {opt_metric}",
                f"{best_row[opt_metric]:.2f}"
            )

            best_col3.metric(
                "Total Return",
                f"{best_row['Total Return (%)']:.2f}%"
            )

            best_col4.metric(
                "Max Drawdown",
                f"{best_row['Max Drawdown (%)']:.2f}%"
            )

            st.subheader("Top 5 Equity Curve Comparison")

            top_labels = optimization_table["Optimization Label"].head(5).tolist()

            fig_opt, ax_opt = plt.subplots(figsize=(12, 6))

            for label in top_labels:
                if label in optimization_curves:
                    curve_data = optimization_curves[label]
                    equity_curve = opt_initial_capital * curve_data["Strategy_Growth"]
                    ax_opt.plot(equity_curve, label=label)

            ax_opt.set_title(f"Top 5 Optimized Strategy Equity Curves - {opt_ticker}")
            ax_opt.set_xlabel("Date")
            ax_opt.set_ylabel("Portfolio Value")
            ax_opt.legend()
            ax_opt.grid(True)

            st.pyplot(fig_opt)

            st.subheader("Top 5 Drawdown Comparison")

            fig_opt_dd, ax_opt_dd = plt.subplots(figsize=(12, 6))

            for label in top_labels:
                if label in optimization_curves:
                    curve_data = optimization_curves[label]
                    ax_opt_dd.plot(
                        curve_data["Strategy_Drawdown"],
                        label=label
                    )

            ax_opt_dd.set_title(f"Top 5 Optimized Strategy Drawdowns - {opt_ticker}")
            ax_opt_dd.set_xlabel("Date")
            ax_opt_dd.set_ylabel("Drawdown")
            ax_opt_dd.legend()
            ax_opt_dd.grid(True)

            st.pyplot(fig_opt_dd)

            optimization_csv = optimization_table.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Optimization Results CSV",
                data=optimization_csv,
                file_name=f"{opt_ticker}_parameter_optimization_results.csv",
                mime="text/csv"
            )


# ==============================
# Portfolio Overview
# ==============================

st.markdown("---")
st.header("Portfolio Overview")
st.write(
    "This section shows the current simulated paper broker account, "
    "open positions, unrealized P&L, and recent paper order activity."
)

# Make sure paper broker, risk manager, and order manager exist in session state
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

portfolio_account = st.session_state.paper_broker.get_account_info()
portfolio_positions = st.session_state.paper_broker.get_positions()

p_col1, p_col2, p_col3, p_col4 = st.columns(4)

p_col1.metric("Paper Cash", f"R {portfolio_account['cash']:,.2f}")
p_col2.metric("Paper Equity", f"R {portfolio_account['equity']:,.2f}")
p_col3.metric("Initial Cash", f"R {portfolio_account['initial_cash']:,.2f}")
p_col4.metric("Open Positions", portfolio_account["open_positions"])

# Calculate total unrealized P&L
if portfolio_positions:
    positions_df = pd.DataFrame(portfolio_positions)
    total_unrealized_pnl = positions_df["unrealized_pnl"].sum()
    total_market_value = positions_df["market_value"].sum()
else:
    positions_df = pd.DataFrame()
    total_unrealized_pnl = 0
    total_market_value = 0

p_col5, p_col6 = st.columns(2)

p_col5.metric("Total Market Value", f"R {total_market_value:,.2f}")
p_col6.metric("Unrealized P&L", f"R {total_unrealized_pnl:,.2f}")

st.subheader("Open Paper Positions")

if positions_df.empty:
    st.info("No open paper positions yet.")
else:
    st.dataframe(positions_df, use_container_width=True)

    # Portfolio allocation chart
    st.subheader("Portfolio Allocation")

    allocation_df = positions_df[["ticker", "market_value"]].copy()
    allocation_df = allocation_df.sort_values(by="market_value", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(
        allocation_df["market_value"],
        labels=allocation_df["ticker"],
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Portfolio Allocation by Market Value")
    ax.axis("equal")

    st.pyplot(fig)

st.subheader("Recent Paper Orders")

order_log_file = PROJECT_PATH / "results" / "order_log.csv"

if order_log_file.exists():
    try:
        portfolio_order_log = pd.read_csv(order_log_file)
        st.dataframe(portfolio_order_log.tail(20), use_container_width=True)

        order_log_csv = portfolio_order_log.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Full Order Log CSV",
            data=order_log_csv,
            file_name="order_log.csv",
            mime="text/csv",
            key="portfolio_order_log_download"
        )

    except Exception as e:
        st.warning("Could not load order log.")
        st.caption(str(e))
else:
    st.info("No order log found yet. Submit a simulated paper order first.")

st.subheader("Portfolio Controls")

if st.button("Reset Paper Broker Portfolio", key="portfolio_reset_button"):
    reset_paper_broker_state(initial_cash=10000)

    st.session_state.paper_broker = PaperBroker(initial_cash=10000)
    st.session_state.order_manager = OrderManager(
        broker=st.session_state.paper_broker,
        risk_manager=st.session_state.risk_manager,
        results_path=PROJECT_PATH / "results"
    )

    st.success("Paper broker portfolio reset successfully.")
    st.rerun()


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

if st.button("Reset Paper Broker Account"):
    reset_paper_broker_state(initial_cash=10000)
    st.session_state.paper_broker = PaperBroker(initial_cash=10000)
    st.session_state.order_manager = OrderManager(
        broker=st.session_state.paper_broker,
        risk_manager=st.session_state.risk_manager,
        results_path=PROJECT_PATH / "results"
    )
    st.success("Paper broker account reset successfully.")
    st.rerun()

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
    [
        "paper_trading_history",
        "order_log",
        "strategy_results",
        "paper_broker_account",
        "paper_broker_positions",
        "paper_broker_orders"
    ]
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
