from trading_control_center import run_trading_control_center_check, get_control_center_step_summary
from test_runner import list_available_tests, run_single_test_script, run_selected_tests, run_safe_test_suite, read_test_results, summarize_test_results, get_test_runner_status
from error_notifier import notify_error, notify_message, read_error_notifications, mark_error_resolved, summarize_errors, get_error_notifier_status
from fill_slippage_tracker import read_order_fills, summarize_slippage, get_fill_slippage_status, record_fill_from_broker_response
from price_validation import validate_order_price_from_proposal, get_price_validation_status
from market_hours import get_market_hours_status, should_allow_market_order_workflow
from broker_account_snapshot import get_broker_account_snapshot, get_snapshot_summary, snapshot_positions_to_dataframe
from position_aware_execution import evaluate_position_aware_proposal, evaluate_position_aware_proposal_with_snapshot, get_positions_from_paper_broker, get_position_aware_status
from order_state_manager import create_order_state_from_proposal, record_broker_submission_state
from duplicate_order_guard import check_duplicate_order_from_proposal, get_duplicate_guard_status, get_active_orders_for_ticker
from order_state_manager import initialize_order_state_tables, read_order_current_states, read_order_state_events, get_order_state_manager_status
from trading_database import initialize_trading_database as sqlite_initialize_trading_database, get_database_status as sqlite_get_database_status, read_table as sqlite_read_table
from trading_database import initialize_trading_database, get_database_status, read_table
from secure_broker_architecture import get_secure_broker_architecture_status
from deployment_health import run_deployment_health_check
from system_health import run_system_health_check
from environment_reset import evaluate_environment_reset, reset_checklist_to_dataframe, bulk_update_reset_checklist, reset_checklist_to_default
from broker_environment import get_environment_recommendation
from live_order_dry_run import run_live_order_dry_run
from live_warning import read_warning_state, acknowledge_live_warning, reset_live_warning_acknowledgement, WARNING_STATEMENTS
from live_mode_lock import evaluate_live_mode_lock, explain_live_mode_lock
from live_readiness import read_readiness_state, update_readiness_item, bulk_update_readiness, evaluate_live_readiness, readiness_to_dataframe
from paper_test_tracker import log_paper_test_event, read_paper_test_log, summarize_paper_test_log, generate_daily_paper_report, save_daily_paper_report, generate_weekly_paper_review, save_weekly_paper_review
from order_proposal import build_order_proposal_from_signal, proposal_to_order_request
from live_signal import generate_live_signal
from trade_audit import log_audit_event
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

# ==============================
# Trading Control Center
# ==============================

st.markdown("---")
st.header("Trading Control Center")
st.write(
    "This is the consolidated pre-trade workflow. It checks signal, proposal, account snapshot, "
    "market hours, position rules, duplicate orders, price validation, and risk before any paper submission."
)

tcc_col1, tcc_col2, tcc_col3, tcc_col4 = st.columns(4)

with tcc_col1:
    tcc_ticker = st.selectbox(
        "Ticker",
        ["SPY", "QQQ", "AAPL", "MSFT"],
        key="tcc_ticker"
    )

with tcc_col2:
    tcc_strategy = st.selectbox(
        "Strategy",
        ["moving_average"],
        key="tcc_strategy"
    )

with tcc_col3:
    tcc_short_window = st.number_input(
        "Short Window",
        min_value=2,
        max_value=100,
        value=20,
        step=1,
        key="tcc_short_window"
    )

with tcc_col4:
    tcc_long_window = st.number_input(
        "Long Window",
        min_value=5,
        max_value=300,
        value=50,
        step=1,
        key="tcc_long_window"
    )

tcc_col5, tcc_col6, tcc_col7, tcc_col8 = st.columns(4)

with tcc_col5:
    tcc_quantity = st.number_input(
        "Quantity",
        min_value=0.0,
        value=1.0,
        step=1.0,
        key="tcc_quantity"
    )

with tcc_col6:
    tcc_order_type = st.selectbox(
        "Order Type",
        ["LMT", "MKT"],
        key="tcc_order_type"
    )

with tcc_col7:
    tcc_limit_price = st.number_input(
        "Limit Price",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.2f",
        key="tcc_limit_price"
    )

with tcc_col8:
    tcc_manual_reference_price = st.number_input(
        "Manual Reference Price",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.2f",
        key="tcc_manual_reference_price"
    )

tcc_allow_after_hours = st.checkbox(
    "Allow after-hours workflow check",
    value=False,
    key="tcc_allow_after_hours"
)

run_tcc_button = st.button(
    "Run Trading Control Center Check",
    key="run_trading_control_center_check"
)

if run_tcc_button:
    try:
        tcc_result = run_trading_control_center_check(
            ticker=tcc_ticker,
            strategy_name=tcc_strategy,
            short_window=tcc_short_window,
            long_window=tcc_long_window,
            quantity=tcc_quantity,
            order_type=tcc_order_type,
            limit_price=tcc_limit_price if tcc_limit_price > 0 else None,
            paper_broker=st.session_state.get("paper_broker"),
            allow_after_hours=tcc_allow_after_hours,
            allow_short_selling=False,
            allow_add_to_existing=False,
            manual_reference_price=tcc_manual_reference_price if tcc_manual_reference_price > 0 else None,
        )

        st.session_state["latest_trading_control_center_result"] = tcc_result

        # Also expose important outputs for other dashboard sections.
        if isinstance(tcc_result.get("workflow_steps", {}).get("signal"), dict):
            st.session_state["latest_live_signal"] = tcc_result["workflow_steps"]["signal"]

        if isinstance(tcc_result.get("workflow_steps", {}).get("order_proposal"), dict):
            st.session_state["latest_order_proposal"] = tcc_result["workflow_steps"]["order_proposal"]

        if isinstance(tcc_result.get("workflow_steps", {}).get("account_snapshot"), dict):
            st.session_state["latest_broker_account_snapshot"] = tcc_result["workflow_steps"]["account_snapshot"]

    except Exception as e:
        st.error("Trading Control Center check failed.")
        st.exception(e)

if "latest_trading_control_center_result" in st.session_state:
    tcc_result = st.session_state["latest_trading_control_center_result"]

    st.subheader("Trading Control Center Decision")

    decision_col1, decision_col2, decision_col3 = st.columns(3)

    decision_col1.metric("Final Decision", tcc_result.get("final_decision"))
    decision_col2.metric("Blockers", len(tcc_result.get("blockers", [])))
    decision_col3.metric("Warnings", len(tcc_result.get("warnings", [])))

    if tcc_result.get("final_decision") == "ready_for_manual_paper_review":
        st.success(tcc_result.get("final_message"))
    else:
        st.error(tcc_result.get("final_message"))

    if tcc_result.get("blockers"):
        st.subheader("Blockers")
        for blocker in tcc_result.get("blockers", []):
            st.error(blocker)

    if tcc_result.get("warnings"):
        st.subheader("Warnings")
        for warning in tcc_result.get("warnings", []):
            st.warning(warning)

    st.subheader("Workflow Step Summary")

    step_summary = get_control_center_step_summary(tcc_result)
    st.dataframe(pd.DataFrame(step_summary), use_container_width=True)

    with st.expander("Full Trading Control Center Result"):
        st.json(tcc_result)



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
# 30-Day IBKR Paper Trading Test
# ==============================

st.markdown("---")
st.header("30-Day IBKR Paper Trading Test")
st.write(
    "Track the IBKR paper trading validation period before considering any live manual trading."
)

paper_summary = summarize_paper_test_log()

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

summary_col1.metric("Total Events", paper_summary.get("total_events", 0))
summary_col2.metric("Unique Test Days", paper_summary.get("unique_test_days", 0))
summary_col3.metric("Signals Reviewed", paper_summary.get("signals_reviewed", 0))
summary_col4.metric("Paper Orders", paper_summary.get("orders_submitted", 0))

summary_col5, summary_col6 = st.columns(2)

summary_col5.metric("Risk Blocks", paper_summary.get("risk_blocks", 0))
summary_col6.metric("Errors", paper_summary.get("errors", 0))

with st.expander("Readiness Status Counts"):
    st.json(paper_summary.get("readiness_status_counts", {}))

st.subheader("Log Paper Test Event")

pt_col1, pt_col2, pt_col3 = st.columns(3)

with pt_col1:
    paper_test_day = st.number_input(
        "Test Day",
        min_value=1,
        max_value=30,
        value=1,
        step=1,
        key="paper_test_day"
    )

with pt_col2:
    paper_test_event_type = st.selectbox(
        "Event Type",
        [
            "DAILY_REVIEW",
            "SIGNAL_REVIEW",
            "PAPER_ORDER_SUBMITTED",
            "RISK_BLOCK",
            "ERROR",
            "POSITION_REVIEW",
            "READINESS_REVIEW",
            "NOTE"
        ],
        key="paper_test_event_type"
    )

with pt_col3:
    paper_test_ticker = st.selectbox(
        "Paper Test Ticker",
        ["SPY", "QQQ", "AAPL", "MSFT", ""],
        key="paper_test_ticker"
    )

pt_col4, pt_col5, pt_col6 = st.columns(3)

with pt_col4:
    paper_test_strategy = st.text_input(
        "Strategy Name",
        value="",
        key="paper_test_strategy"
    )

with pt_col5:
    paper_test_signal = st.selectbox(
        "Signal",
        ["", "BUY", "SELL", "HOLD", "STAY IN CASH"],
        key="paper_test_signal"
    )

with pt_col6:
    paper_test_order_status = st.selectbox(
        "Broker Order Status",
        ["", "not_submitted", "submitted", "filled", "cancelled", "rejected", "blocked"],
        key="paper_test_order_status"
    )

pt_col7, pt_col8, pt_col9 = st.columns(3)

with pt_col7:
    paper_test_proposal_status = st.selectbox(
        "Proposal Status",
        ["", "no_order", "proposed", "blocked_quantity_zero", "blocked_no_position_to_sell"],
        key="paper_test_proposal_status"
    )

with pt_col8:
    paper_test_risk_status = st.selectbox(
        "Risk Status",
        ["", "approved", "blocked", "not_required"],
        key="paper_test_risk_status"
    )

with pt_col9:
    paper_test_manual_decision = st.selectbox(
        "Manual Decision",
        ["", "reviewed", "approved", "rejected", "skipped"],
        key="paper_test_manual_decision"
    )

paper_order_id = st.text_input(
    "Order ID",
    value="",
    key="paper_order_id"
)

paper_position_status = st.text_input(
    "Position Status",
    value="",
    key="paper_position_status"
)

paper_pnl_note = st.text_area(
    "P&L Note",
    value="",
    key="paper_pnl_note"
)

paper_error_note = st.text_area(
    "Error Note",
    value="",
    key="paper_error_note"
)

paper_review_note = st.text_area(
    "Review Note",
    value="",
    key="paper_review_note"
)

paper_readiness_status = st.selectbox(
    "Readiness Status",
    [
        "not_reviewed",
        "not_ready",
        "needs_more_testing",
        "paper_ready",
        "live_not_recommended",
        "small_live_test_candidate"
    ],
    key="paper_readiness_status"
)

log_paper_test_button = st.button(
    "Log 30-Day Paper Test Event",
    key="log_30_day_paper_test_event"
)

if log_paper_test_button:
    result = log_paper_test_event(
        test_day=paper_test_day,
        event_type=paper_test_event_type,
        ticker=paper_test_ticker or None,
        strategy_name=paper_test_strategy or None,
        signal=paper_test_signal or None,
        proposal_status=paper_test_proposal_status or None,
        risk_status=paper_test_risk_status or None,
        manual_decision=paper_test_manual_decision or None,
        broker_order_status=paper_test_order_status or None,
        order_id=paper_order_id or None,
        position_status=paper_position_status or None,
        pnl_note=paper_pnl_note or None,
        error_note=paper_error_note or None,
        review_note=paper_review_note or None,
        readiness_status=paper_readiness_status,
        details={
            "source": "streamlit_dashboard",
            "execution_mode": EXECUTION_MODE,
            "default_broker": DEFAULT_BROKER
        }
    )

    st.success("Paper test event logged.")
    st.caption(result["log_file"])
    st.rerun()

st.subheader("Latest Paper Test Log")

paper_log_df = read_paper_test_log(limit=50)

if paper_log_df.empty:
    st.info("No paper test log records found yet.")
else:
    st.dataframe(paper_log_df, use_container_width=True)

    paper_log_csv = paper_log_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Latest Paper Test Log CSV",
        data=paper_log_csv,
        file_name="paper_trading_30_day_log_latest.csv",
        mime="text/csv",
        key="download_paper_test_log_csv"
    )




# ==============================
# Daily Paper Trading Report
# ==============================

st.markdown("---")
st.header("Daily Paper Trading Report")
st.write(
    "Generate a daily summary from the 30-day IBKR paper trading test log."
)

daily_report_col1, daily_report_col2 = st.columns(2)

with daily_report_col1:
    daily_report_day = st.number_input(
        "Daily Report Test Day",
        min_value=1,
        max_value=30,
        value=1,
        step=1,
        key="daily_report_day"
    )

with daily_report_col2:
    use_latest_day = st.checkbox(
        "Use latest available test day",
        value=False,
        key="use_latest_day_for_daily_report"
    )

generate_daily_report_button = st.button(
    "Generate Daily Paper Trading Report",
    key="generate_daily_paper_trading_report"
)

if generate_daily_report_button:
    selected_day = None if use_latest_day else daily_report_day

    daily_report_result = generate_daily_paper_report(test_day=selected_day)

    if not daily_report_result.get("has_data"):
        st.warning(daily_report_result.get("message"))
    else:
        report = daily_report_result["report"]

        st.success(daily_report_result.get("message"))

        report_col1, report_col2, report_col3, report_col4 = st.columns(4)

        report_col1.metric("Test Day", report.get("test_day"))
        report_col2.metric("Total Events", report.get("total_events"))
        report_col3.metric("Signals Reviewed", report.get("signals_reviewed"))
        report_col4.metric("Paper Orders", report.get("paper_orders_submitted"))

        report_col5, report_col6 = st.columns(2)

        report_col5.metric("Risk Blocks", report.get("risk_blocks"))
        report_col6.metric("Errors", report.get("errors"))

        st.subheader("Event Counts")
        st.json(report.get("event_counts", {}))

        st.subheader("Signal Counts")
        st.json(report.get("signal_counts", {}))

        st.subheader("Risk Status Counts")
        st.json(report.get("risk_status_counts", {}))

        st.subheader("Broker Order Status Counts")
        st.json(report.get("broker_order_status_counts", {}))

        st.subheader("Readiness Status Counts")
        st.json(report.get("readiness_status_counts", {}))

        st.subheader("Latest Notes")

        latest_notes = report.get("latest_notes", [])

        if latest_notes:
            st.dataframe(pd.DataFrame(latest_notes), use_container_width=True)
        else:
            st.info("No notes found for this report.")

        st.session_state["latest_daily_paper_report"] = report

save_daily_report_button = st.button(
    "Save Daily Paper Trading Report",
    key="save_daily_paper_trading_report"
)

if save_daily_report_button:
    selected_day = None if use_latest_day else daily_report_day

    save_result = save_daily_paper_report(test_day=selected_day)

    st.success("Daily paper trading report saved.")
    st.caption(save_result["report_file"])

if "latest_daily_paper_report" in st.session_state:
    latest_report = st.session_state["latest_daily_paper_report"]

    report_csv_df = pd.DataFrame([{
        "test_day": latest_report.get("test_day"),
        "date_generated": latest_report.get("date_generated"),
        "total_events": latest_report.get("total_events"),
        "signals_reviewed": latest_report.get("signals_reviewed"),
        "paper_orders_submitted": latest_report.get("paper_orders_submitted"),
        "risk_blocks": latest_report.get("risk_blocks"),
        "errors": latest_report.get("errors"),
        "event_counts": str(latest_report.get("event_counts")),
        "signal_counts": str(latest_report.get("signal_counts")),
        "risk_status_counts": str(latest_report.get("risk_status_counts")),
        "manual_decision_counts": str(latest_report.get("manual_decision_counts")),
        "broker_order_status_counts": str(latest_report.get("broker_order_status_counts")),
        "readiness_status_counts": str(latest_report.get("readiness_status_counts")),
        "latest_notes": str(latest_report.get("latest_notes"))
    }])

    report_csv = report_csv_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Daily Report CSV",
        data=report_csv,
        file_name="daily_paper_trading_report.csv",
        mime="text/csv",
        key="download_daily_paper_report_csv"
    )




# ==============================
# Weekly Paper Trading Review
# ==============================

st.markdown("---")
st.header("Weekly Paper Trading Review")
st.write(
    "Review weekly progress from the 30-day IBKR paper trading validation period."
)

weekly_review_col1, weekly_review_col2 = st.columns(2)

with weekly_review_col1:
    weekly_review_number = st.number_input(
        "Weekly Review Number",
        min_value=1,
        max_value=4,
        value=1,
        step=1,
        key="weekly_review_number"
    )

with weekly_review_col2:
    use_latest_week = st.checkbox(
        "Use latest available week",
        value=False,
        key="use_latest_week_for_review"
    )

generate_weekly_review_button = st.button(
    "Generate Weekly Paper Trading Review",
    key="generate_weekly_paper_trading_review"
)

if generate_weekly_review_button:
    selected_week = None if use_latest_week else weekly_review_number

    weekly_review_result = generate_weekly_paper_review(week_number=selected_week)

    if not weekly_review_result.get("has_data"):
        st.warning(weekly_review_result.get("message"))
    else:
        review = weekly_review_result["review"]

        st.success(weekly_review_result.get("message"))

        wr_col1, wr_col2, wr_col3, wr_col4 = st.columns(4)

        wr_col1.metric("Week", review.get("week_number"))
        wr_col2.metric("Total Events", review.get("total_events"))
        wr_col3.metric("Signals Reviewed", review.get("signals_reviewed"))
        wr_col4.metric("Paper Orders", review.get("paper_orders_submitted"))

        wr_col5, wr_col6, wr_col7 = st.columns(3)

        wr_col5.metric("Risk Blocks", review.get("risk_blocks"))
        wr_col6.metric("Errors", review.get("errors"))
        wr_col7.metric("Weekly Status", review.get("weekly_status"))

        st.subheader("Recommendation")

        weekly_status = review.get("weekly_status")

        if weekly_status in ["needs_debugging", "insufficient_activity"]:
            st.warning(review.get("recommendation"))
        elif weekly_status == "paper_execution_working":
            st.success(review.get("recommendation"))
        else:
            st.info(review.get("recommendation"))

        st.subheader("Test Days Included")
        st.write(review.get("test_days_included"))

        st.subheader("Event Counts")
        st.json(review.get("event_counts", {}))

        st.subheader("Signal Counts")
        st.json(review.get("signal_counts", {}))

        st.subheader("Risk Status Counts")
        st.json(review.get("risk_status_counts", {}))

        st.subheader("Broker Order Status Counts")
        st.json(review.get("broker_order_status_counts", {}))

        st.subheader("Readiness Status Counts")
        st.json(review.get("readiness_status_counts", {}))

        st.subheader("Important Notes")

        important_notes = review.get("important_notes", [])

        if important_notes:
            st.dataframe(pd.DataFrame(important_notes), use_container_width=True)
        else:
            st.info("No important notes found for this week.")

        st.session_state["latest_weekly_paper_review"] = review

save_weekly_review_button = st.button(
    "Save Weekly Paper Trading Review",
    key="save_weekly_paper_trading_review"
)

if save_weekly_review_button:
    selected_week = None if use_latest_week else weekly_review_number

    save_result = save_weekly_paper_review(week_number=selected_week)

    st.success("Weekly paper trading review saved.")
    st.caption(save_result["review_file"])

if "latest_weekly_paper_review" in st.session_state:
    latest_weekly_review = st.session_state["latest_weekly_paper_review"]

    weekly_review_csv_df = pd.DataFrame([{
        "week_number": latest_weekly_review.get("week_number"),
        "date_generated": latest_weekly_review.get("date_generated"),
        "test_days_included": str(latest_weekly_review.get("test_days_included")),
        "total_events": latest_weekly_review.get("total_events"),
        "signals_reviewed": latest_weekly_review.get("signals_reviewed"),
        "paper_orders_submitted": latest_weekly_review.get("paper_orders_submitted"),
        "risk_blocks": latest_weekly_review.get("risk_blocks"),
        "errors": latest_weekly_review.get("errors"),
        "weekly_status": latest_weekly_review.get("weekly_status"),
        "recommendation": latest_weekly_review.get("recommendation"),
        "event_counts": str(latest_weekly_review.get("event_counts")),
        "signal_counts": str(latest_weekly_review.get("signal_counts")),
        "risk_status_counts": str(latest_weekly_review.get("risk_status_counts")),
        "broker_order_status_counts": str(latest_weekly_review.get("broker_order_status_counts")),
        "readiness_status_counts": str(latest_weekly_review.get("readiness_status_counts")),
        "important_notes": str(latest_weekly_review.get("important_notes"))
    }])

    weekly_review_csv = weekly_review_csv_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Weekly Review CSV",
        data=weekly_review_csv,
        file_name="weekly_paper_trading_review.csv",
        mime="text/csv",
        key="download_weekly_paper_review_csv"
    )




# ==============================
# Live Trading Readiness Checklist
# ==============================

st.markdown("---")
st.header("Live Trading Readiness Checklist")
st.write(
    "This checklist must be completed before very small live manual testing can even be considered. "
    "It does not enable live trading."
)

readiness_eval = evaluate_live_readiness()

readiness_col1, readiness_col2, readiness_col3, readiness_col4 = st.columns(4)

readiness_col1.metric("Readiness Status", readiness_eval.get("status"))
readiness_col2.metric("Readiness Score", f"{readiness_eval.get('readiness_score', 0) * 100:.1f}%")
readiness_col3.metric("Completed", readiness_eval.get("completed_count"))
readiness_col4.metric("Missing", readiness_eval.get("missing_count"))

if readiness_eval.get("ready_for_small_live_test"):
    st.success(readiness_eval.get("recommendation"))
else:
    st.warning(readiness_eval.get("recommendation"))

with st.expander("Missing Readiness Items"):
    st.write(readiness_eval.get("missing_items", []))

with st.expander("Completed Readiness Items"):
    st.write(readiness_eval.get("completed_items", []))

st.subheader("Checklist Items")

readiness_df = readiness_to_dataframe()

edited_readiness_df = st.data_editor(
    readiness_df,
    use_container_width=True,
    hide_index=True,
    key="live_readiness_editor"
)

readiness_notes = st.text_area(
    "Readiness Notes",
    value=readiness_eval.get("notes", ""),
    key="live_readiness_notes"
)

save_readiness_button = st.button(
    "Save Live Readiness Checklist",
    key="save_live_readiness_checklist"
)

if save_readiness_button:
    updates = {}

    for _, row in edited_readiness_df.iterrows():
        updates[row["checklist_item"]] = bool(row["completed"])

    bulk_update_readiness(
        checklist_updates=updates,
        updated_by="streamlit_dashboard",
        notes=readiness_notes
    )

    st.success("Live readiness checklist saved.")
    st.rerun()

st.subheader("Live Readiness Final Warning")

if readiness_eval.get("ready_for_small_live_test"):
    st.error(
        "Even if the checklist is complete, this does NOT enable live trading. "
        "The next phase still requires a live mode lock, warning screen, dry-run mode, "
        "and very small manual testing plan."
    )
else:
    st.info(
        "Live trading remains blocked. Continue paper testing until every required item is complete."
    )






# ==============================
# Live Trading Warning Screen
# ==============================

st.markdown("---")
st.header("Live Trading Warning Screen")
st.write(
    "This warning must be acknowledged before very small live manual testing can ever be considered. "
    "Acknowledgement does not enable live trading."
)

warning_state = read_warning_state()

if warning_state.get("acknowledged", False):
    st.success(
        f"Live trading warning acknowledged by {warning_state.get('acknowledged_by', '')} "
        f"at {warning_state.get('acknowledged_at', '')}."
    )
else:
    st.warning("Live trading warning has not been acknowledged.")

st.subheader("Live Trading Risk Statements")

warning_checks = []

for idx, statement in enumerate(WARNING_STATEMENTS):
    checked = st.checkbox(
        statement,
        key=f"live_warning_statement_{idx}"
    )
    warning_checks.append(checked)

warning_notes = st.text_area(
    "Warning Acknowledgement Notes",
    value=warning_state.get("notes", ""),
    key="live_warning_notes"
)

acknowledge_warning_button = st.button(
    "Acknowledge Live Trading Warning",
    key="acknowledge_live_trading_warning"
)

if acknowledge_warning_button:
    if not all(warning_checks):
        st.error("You must tick every warning statement before acknowledgement can be saved.")
    else:
        acknowledge_live_warning(
            acknowledged_by="streamlit_dashboard",
            notes=warning_notes
        )

        log_audit_event(
            event_type="LIVE_WARNING_ACKNOWLEDGED",
            broker_name="ibkr",
            execution_mode=EXECUTION_MODE,
            broker_status="not_submitted",
            message="Live trading warning acknowledged in dashboard.",
            details={
                "statements": WARNING_STATEMENTS,
                "notes": warning_notes
            }
        )

        st.success("Live trading warning acknowledgement saved.")
        st.rerun()

reset_warning_button = st.button(
    "Reset Live Warning Acknowledgement",
    key="reset_live_warning_acknowledgement"
)

if reset_warning_button:
    reset_live_warning_acknowledgement()

    log_audit_event(
        event_type="LIVE_WARNING_ACKNOWLEDGEMENT_RESET",
        broker_name="ibkr",
        execution_mode=EXECUTION_MODE,
        broker_status="not_submitted",
        message="Live trading warning acknowledgement reset in dashboard."
    )

    st.warning("Live warning acknowledgement reset.")
    st.rerun()

with st.expander("Live Warning State"):
    st.json(warning_state)


# ==============================
# Live Mode Lock
# ==============================

st.markdown("---")
st.header("Live Mode Lock")
st.write(
    "This lock prevents live trading from being enabled accidentally. "
    "All required conditions must pass before very small live manual testing can even be considered."
)

live_lock_eval = evaluate_live_mode_lock()

lock_col1, lock_col2, lock_col3 = st.columns(3)

lock_col1.metric("Live Lock Status", live_lock_eval.get("status"))
lock_col2.metric("Live Mode Allowed", str(live_lock_eval.get("live_mode_allowed")))
lock_col3.metric("Failed Checks", len(live_lock_eval.get("failed_checks", [])))

if live_lock_eval.get("live_mode_allowed"):
    st.error(
        "Live mode lock is UNLOCKED. This does not allow automated trading. "
        "Proceed only with final warning, dry run, and very small manual testing plan."
    )
else:
    st.success("Live mode is locked. This is the expected safe state for now.")

st.subheader("Live Mode Lock Message")
st.write(live_lock_eval.get("message"))

st.subheader("Failed Checks")

failed_checks = live_lock_eval.get("failed_checks", [])

if failed_checks:
    st.warning("The following checks are currently blocking live mode:")
    st.write(failed_checks)
else:
    st.success("No failed checks.")

with st.expander("Passed Checks"):
    st.write(live_lock_eval.get("passed_checks", []))

with st.expander("Full Live Mode Lock Evaluation"):
    st.json(live_lock_eval)

st.subheader("Live Mode Lock Guidance")

st.info(
    "For now, this should remain locked. The next steps are warning screen, dry-run mode, "
    "and only later very small manual live testing after all reviews are complete."
)




# ==============================
# Live Order Dry Run Mode
# ==============================

st.markdown("---")
st.header("Live Order Dry Run Mode")
st.write(
    "Build and validate a future live order without submitting it to IBKR. "
    "This is a safety simulation only."
)

st.warning(
    "Dry run mode does not place trades. It does not enable live trading. "
    "It only checks whether the proposed live order would pass current safety gates."
)

latest_order_proposal_for_dry_run = st.session_state.get("latest_order_proposal", {})

use_latest_proposal_for_dry_run = False

if latest_order_proposal_for_dry_run and latest_order_proposal_for_dry_run.get("actionable", False):
    use_latest_proposal_for_dry_run = st.checkbox(
        "Use latest actionable order proposal for dry run",
        value=True,
        key="use_latest_proposal_for_live_dry_run"
    )
else:
    st.info("No actionable order proposal is available. You can still enter dry-run details manually.")

dry_col1, dry_col2, dry_col3 = st.columns(3)

with dry_col1:
    dry_ticker_default = latest_order_proposal_for_dry_run.get("ticker", "SPY") if use_latest_proposal_for_dry_run else "SPY"
    dry_ticker_options = ["SPY", "QQQ", "AAPL", "MSFT"]

    if dry_ticker_default not in dry_ticker_options:
        dry_ticker_default = "SPY"

    dry_run_ticker = st.selectbox(
        "Dry Run Ticker",
        dry_ticker_options,
        index=dry_ticker_options.index(dry_ticker_default),
        key="dry_run_ticker"
    )

with dry_col2:
    dry_side_default = latest_order_proposal_for_dry_run.get("side", "BUY") if use_latest_proposal_for_dry_run else "BUY"
    dry_side_options = ["BUY", "SELL"]

    if dry_side_default not in dry_side_options:
        dry_side_default = "BUY"

    dry_run_side = st.selectbox(
        "Dry Run Side",
        dry_side_options,
        index=dry_side_options.index(dry_side_default),
        key="dry_run_side"
    )

with dry_col3:
    dry_asset_default = latest_order_proposal_for_dry_run.get("asset_type", "etf") if use_latest_proposal_for_dry_run else "etf"
    dry_asset_options = ["etf", "stock"]

    if dry_asset_default not in dry_asset_options:
        dry_asset_default = "etf"

    dry_run_asset_type = st.selectbox(
        "Dry Run Asset Type",
        dry_asset_options,
        index=dry_asset_options.index(dry_asset_default),
        key="dry_run_asset_type"
    )

dry_col4, dry_col5, dry_col6 = st.columns(3)

with dry_col4:
    dry_quantity_default = float(latest_order_proposal_for_dry_run.get("quantity", 1.0)) if use_latest_proposal_for_dry_run else 1.0

    dry_run_quantity = st.number_input(
        "Dry Run Quantity",
        min_value=0.0,
        value=dry_quantity_default,
        step=1.0,
        key="dry_run_quantity"
    )

with dry_col5:
    dry_order_type_default = latest_order_proposal_for_dry_run.get("order_type", "LMT") if use_latest_proposal_for_dry_run else "LMT"
    dry_order_type_options = ["LMT", "MKT"]

    if dry_order_type_default not in dry_order_type_options:
        dry_order_type_default = "LMT"

    dry_run_order_type = st.selectbox(
        "Dry Run Order Type",
        dry_order_type_options,
        index=dry_order_type_options.index(dry_order_type_default),
        key="dry_run_order_type"
    )

with dry_col6:
    dry_limit_default = latest_order_proposal_for_dry_run.get("limit_price", 1.00) if use_latest_proposal_for_dry_run else 1.00

    if dry_limit_default is None:
        dry_limit_default = 1.00

    dry_run_limit_price = st.number_input(
        "Dry Run Limit Price",
        min_value=0.0,
        value=float(dry_limit_default),
        step=0.01,
        format="%.2f",
        key="dry_run_limit_price"
    )

dry_col7, dry_col8, dry_col9 = st.columns(3)

with dry_col7:
    dry_run_position_size = st.slider(
        "Dry Run Proposed Position Size",
        min_value=0.001,
        max_value=0.10,
        value=0.01,
        step=0.001,
        key="dry_run_position_size"
    )

with dry_col8:
    dry_current_position_quantity = st.number_input(
        "Dry Run Current Position Quantity",
        min_value=0.0,
        value=0.0,
        step=1.0,
        key="dry_current_position_quantity"
    )

with dry_col9:
    dry_run_manual_confirmation = st.checkbox(
        "Dry Run Manual Confirmation Given",
        value=False,
        key="dry_run_manual_confirmation"
    )

run_dry_run_button = st.button(
    "Run Live Order Dry Run",
    key="run_live_order_dry_run_button"
)

if run_dry_run_button:
    try:
        estimated_price = dry_run_limit_price if dry_run_order_type == "LMT" else None
        estimated_order_value = None

        if estimated_price is not None:
            estimated_order_value = float(dry_run_quantity) * float(estimated_price)

        dry_run_result = run_live_order_dry_run(
            ticker=dry_run_ticker,
            side=dry_run_side,
            quantity=dry_run_quantity,
            order_type=dry_run_order_type,
            limit_price=dry_run_limit_price if dry_run_order_type == "LMT" else None,
            asset_type=dry_run_asset_type,
            proposed_position_size=dry_run_position_size,
            estimated_price=estimated_price,
            estimated_order_value=estimated_order_value,
            current_position_quantity=dry_current_position_quantity,
            manual_confirmation_given=dry_run_manual_confirmation,
            strategy_name=latest_order_proposal_for_dry_run.get("strategy_label") if use_latest_proposal_for_dry_run else "manual_dry_run",
            signal=latest_order_proposal_for_dry_run.get("signal_action") if use_latest_proposal_for_dry_run else None
        )

        st.session_state["latest_live_order_dry_run"] = dry_run_result

        if dry_run_result.get("dry_run_passed"):
            st.success("Dry run passed. No order was submitted.")
        else:
            st.warning("Dry run blocked. No order was submitted.")

        st.subheader("Dry Run Recommendation")
        st.write(dry_run_result.get("recommendation"))

        st.subheader("Dry Run Blockers")
        blockers = dry_run_result.get("blockers", [])

        if blockers:
            st.write(blockers)
        else:
            st.success("No blockers found.")

        with st.expander("Full Dry Run Report"):
            st.json(dry_run_result)

        log_audit_event(
            event_type="LIVE_ORDER_DRY_RUN_COMPLETED",
            ticker=dry_run_ticker,
            side=dry_run_side,
            quantity=dry_run_quantity,
            order_type=dry_run_order_type,
            limit_price=dry_run_limit_price if dry_run_order_type == "LMT" else None,
            strategy_name=latest_order_proposal_for_dry_run.get("strategy_label") if use_latest_proposal_for_dry_run else "manual_dry_run",
            signal=latest_order_proposal_for_dry_run.get("signal_action") if use_latest_proposal_for_dry_run else None,
            risk_approved=dry_run_result.get("risk_check", {}).get("approved"),
            risk_reason=dry_run_result.get("risk_check", {}).get("reason"),
            manual_confirmation=dry_run_manual_confirmation,
            broker_name="ibkr",
            execution_mode=EXECUTION_MODE,
            broker_status="dry_run_only",
            message="Live order dry run completed. No order submitted.",
            details=dry_run_result
        )

    except Exception as e:
        st.error("Live order dry run failed.")
        st.exception(e)

if "latest_live_order_dry_run" in st.session_state:
    st.subheader("Latest Live Order Dry Run Summary")

    latest_dry_run = st.session_state["latest_live_order_dry_run"]

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    summary_col1.metric("Dry Run Passed", str(latest_dry_run.get("dry_run_passed")))
    summary_col2.metric("Submitted to Broker", str(latest_dry_run.get("submitted_to_broker")))
    summary_col3.metric("Blocker Count", len(latest_dry_run.get("blockers", [])))






# ==============================
# Environment Reset Checklist
# ==============================

st.markdown("---")
st.header("Environment Reset Checklist")
st.write(
    "Use this after IBKR paper order testing or live read-only checks to confirm "
    "that the system has been returned to a safer state."
)

reset_eval = evaluate_environment_reset()

reset_col1, reset_col2, reset_col3, reset_col4 = st.columns(4)

reset_col1.metric("Reset Status", reset_eval.get("status"))
reset_col2.metric("Reset Score", f"{reset_eval.get('reset_score', 0) * 100:.1f}%")
reset_col3.metric("Completed", reset_eval.get("completed_count"))
reset_col4.metric("Missing", reset_eval.get("missing_count"))

if reset_eval.get("reset_complete"):
    st.success(reset_eval.get("recommendation"))
else:
    st.warning(reset_eval.get("recommendation"))

with st.expander("Missing Reset Items"):
    st.write(reset_eval.get("missing_items", []))

with st.expander("Completed Reset Items"):
    st.write(reset_eval.get("completed_items", []))

st.subheader("Reset Checklist Items")

reset_df = reset_checklist_to_dataframe()

edited_reset_df = st.data_editor(
    reset_df,
    use_container_width=True,
    hide_index=True,
    key="environment_reset_editor"
)

reset_notes = st.text_area(
    "Environment Reset Notes",
    value=reset_eval.get("notes", ""),
    key="environment_reset_notes"
)

save_reset_button = st.button(
    "Save Environment Reset Checklist",
    key="save_environment_reset_checklist"
)

if save_reset_button:
    updates = {}

    for _, row in edited_reset_df.iterrows():
        updates[row["reset_item"]] = bool(row["completed"])

    bulk_update_reset_checklist(
        checklist_updates=updates,
        updated_by="streamlit_dashboard",
        notes=reset_notes
    )

    log_audit_event(
        event_type="ENVIRONMENT_RESET_CHECKLIST_SAVED",
        broker_name="ibkr",
        execution_mode=EXECUTION_MODE,
        broker_status="not_submitted",
        message="Environment reset checklist saved.",
        details={
            "updates": updates,
            "notes": reset_notes
        }
    )

    st.success("Environment reset checklist saved.")
    st.rerun()

reset_default_button = st.button(
    "Reset Environment Checklist to Default",
    key="reset_environment_checklist_to_default"
)

if reset_default_button:
    reset_checklist_to_default()

    log_audit_event(
        event_type="ENVIRONMENT_RESET_CHECKLIST_RESET",
        broker_name="ibkr",
        execution_mode=EXECUTION_MODE,
        broker_status="not_submitted",
        message="Environment reset checklist reset to default."
    )

    st.warning("Environment reset checklist reset.")
    st.rerun()

st.subheader("Manual Reset Guidance")

st.info(
    "Recommended safe reset after paper order testing: set IBKR_READ_ONLY=true, "
    "set IBKR_ENABLE_ORDERS=false, confirm ALLOW_LIVE_TRADING=False, "
    "confirm LIVE_TRADING_ENABLED=False, restart Streamlit, and check the Broker Environment Safety Panel."
)


# ==============================
# Broker Environment Safety Panel
# ==============================

st.markdown("---")
st.header("Broker Environment Safety Panel")
st.write(
    "Review the current broker environment before running any broker-related workflow. "
    "This panel does not change settings."
)

env_result = get_environment_recommendation()

env_col1, env_col2, env_col3 = st.columns(3)

env_col1.metric("Environment Status", env_result.get("status"))
env_col2.metric("Safe", str(env_result.get("safe")))
env_col3.metric("Blockers", len(env_result.get("blockers", [])))

if env_result.get("safe"):
    st.success(env_result.get("message"))
else:
    st.error(env_result.get("message"))

st.subheader("Environment Recommendation")
st.info(env_result.get("recommendation"))

warnings_list = env_result.get("warnings", [])
blockers_list = env_result.get("blockers", [])

if warnings_list:
    st.subheader("Warnings")
    st.warning(warnings_list)

if blockers_list:
    st.subheader("Blockers")
    st.error(blockers_list)

with st.expander("Current Broker Environment Snapshot"):
    st.json(env_result.get("snapshot", {}))

st.caption(
    "To change broker environment, update your local .env/config settings intentionally, "
    "then restart Streamlit. This panel is display-only."
)




# ==============================
# Market Hours Awareness
# ==============================

st.markdown("---")
st.header("Market Hours Awareness")
st.write(
    "Check whether the US market is currently open before allowing signal or order workflows."
)

refresh_market_hours_button = st.button(
    "Refresh Market Hours Status",
    key="refresh_market_hours_status_button"
)

if refresh_market_hours_button or "latest_market_hours_status" not in st.session_state:
    st.session_state["latest_market_hours_status"] = get_market_hours_status()

market_hours_status = st.session_state["latest_market_hours_status"]

us_market = market_hours_status.get("us_market", {})
workflow_status = market_hours_status.get("regular_order_workflow", {})

mh_col1, mh_col2, mh_col3, mh_col4 = st.columns(4)

mh_col1.metric("US Market Open", str(us_market.get("is_open")))
mh_col2.metric("Session Status", us_market.get("session_status"))
mh_col3.metric("Workflow Allowed", str(workflow_status.get("allowed")))
mh_col4.metric("Exchange", us_market.get("exchange"))

st.write("US Eastern Time:", market_hours_status.get("checked_at_us_eastern"))
st.write("South Africa Time:", market_hours_status.get("checked_at_south_africa"))

if workflow_status.get("allowed"):
    st.success(workflow_status.get("reason"))
else:
    st.warning(workflow_status.get("reason"))

if us_market.get("market_open_et"):
    st.write("Market Open ET:", us_market.get("market_open_et"))

if us_market.get("market_close_et"):
    st.write("Market Close ET:", us_market.get("market_close_et"))

if us_market.get("next_open_et"):
    st.write("Next Open ET:", us_market.get("next_open_et"))

if us_market.get("warning"):
    st.warning(us_market.get("warning"))

with st.expander("Full Market Hours Status"):
    st.json(market_hours_status)


# ==============================
# Live Broker Signal Generator
# ==============================

st.markdown("---")
st.header("Live Broker Signal Generator")
st.write(
    "Generate the latest strategy signal for review. "
    "This does not submit any broker order."
)

signal_col1, signal_col2, signal_col3 = st.columns(3)

with signal_col1:
    signal_ticker = st.selectbox(
        "Signal Ticker",
        ["SPY", "QQQ", "AAPL", "MSFT"],
        key="signal_ticker"
    )

with signal_col2:
    signal_strategy = st.selectbox(
        "Signal Strategy",
        [
            "moving_average",
            "rsi",
            "bollinger_bands",
            "momentum",
            "breakout"
        ],
        key="signal_strategy"
    )

with signal_col3:
    signal_start_date = st.text_input(
        "Signal Start Date",
        value="2018-01-01",
        key="signal_start_date"
    )

signal_param_col1, signal_param_col2, signal_param_col3 = st.columns(3)

with signal_param_col1:
    signal_position_size = st.slider(
        "Signal Position Size",
        min_value=0.10,
        max_value=1.00,
        value=0.50,
        step=0.05,
        key="signal_position_size"
    )

with signal_param_col2:
    signal_trading_cost = st.number_input(
        "Signal Trading Cost",
        min_value=0.0,
        max_value=0.05,
        value=0.001,
        step=0.001,
        format="%.4f",
        key="signal_trading_cost"
    )

with signal_param_col3:
    signal_regime_window = st.number_input(
        "Signal Regime Window",
        min_value=50,
        max_value=300,
        value=200,
        step=10,
        key="signal_regime_window"
    )

st.subheader("Strategy Parameters")

if signal_strategy == "moving_average":
    sig_col_a, sig_col_b = st.columns(2)

    with sig_col_a:
        signal_short_window = st.number_input(
            "Signal Short MA",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            key="signal_short_window"
        )

    with sig_col_b:
        signal_long_window = st.number_input(
            "Signal Long MA",
            min_value=20,
            max_value=300,
            value=50,
            step=10,
            key="signal_long_window"
        )

else:
    signal_short_window = 20
    signal_long_window = 50

if signal_strategy == "rsi":
    rsi_col_a, rsi_col_b, rsi_col_c = st.columns(3)

    with rsi_col_a:
        signal_rsi_window = st.number_input(
            "Signal RSI Window",
            min_value=5,
            max_value=50,
            value=14,
            step=1,
            key="signal_rsi_window"
        )

    with rsi_col_b:
        signal_oversold_level = st.number_input(
            "Signal Oversold Level",
            min_value=5,
            max_value=50,
            value=30,
            step=5,
            key="signal_oversold_level"
        )

    with rsi_col_c:
        signal_overbought_level = st.number_input(
            "Signal Overbought Level",
            min_value=50,
            max_value=95,
            value=70,
            step=5,
            key="signal_overbought_level"
        )

else:
    signal_rsi_window = 14
    signal_oversold_level = 30
    signal_overbought_level = 70

if signal_strategy == "bollinger_bands":
    bb_col_a, bb_col_b = st.columns(2)

    with bb_col_a:
        signal_bollinger_window = st.number_input(
            "Signal Bollinger Window",
            min_value=10,
            max_value=100,
            value=20,
            step=5,
            key="signal_bollinger_window"
        )

    with bb_col_b:
        signal_bollinger_std = st.number_input(
            "Signal Bollinger Std",
            min_value=1.0,
            max_value=4.0,
            value=2.0,
            step=0.5,
            key="signal_bollinger_std"
        )

else:
    signal_bollinger_window = 20
    signal_bollinger_std = 2.0

if signal_strategy == "momentum":
    signal_momentum_window = st.number_input(
        "Signal Momentum Window",
        min_value=10,
        max_value=200,
        value=60,
        step=10,
        key="signal_momentum_window"
    )
else:
    signal_momentum_window = 60

if signal_strategy == "breakout":
    breakout_col_a, breakout_col_b = st.columns(2)

    with breakout_col_a:
        signal_breakout_window = st.number_input(
            "Signal Breakout Window",
            min_value=20,
            max_value=250,
            value=50,
            step=10,
            key="signal_breakout_window"
        )

    with breakout_col_b:
        signal_exit_window = st.number_input(
            "Signal Exit Window",
            min_value=10,
            max_value=150,
            value=20,
            step=10,
            key="signal_exit_window"
        )

else:
    signal_breakout_window = 50
    signal_exit_window = 20

generate_signal_button = st.button(
    "Generate Latest Signal",
    key="generate_latest_signal_button"
)

if generate_signal_button:
    try:
        with st.spinner("Generating latest strategy signal..."):
            signal_result, signal_data, signal_summary, signal_trade_log = generate_live_signal(
                ticker=signal_ticker,
                strategy_name=signal_strategy,
                start_date=signal_start_date,
                end_date=None,
                initial_capital=10000,
                position_size=signal_position_size,
                trading_cost=signal_trading_cost,
                regime_window=int(signal_regime_window),
                short_window=int(signal_short_window),
                long_window=int(signal_long_window),
                rsi_window=int(signal_rsi_window),
                oversold_level=int(signal_oversold_level),
                overbought_level=int(signal_overbought_level),
                bollinger_window=int(signal_bollinger_window),
                bollinger_std=float(signal_bollinger_std),
                momentum_window=int(signal_momentum_window),
                breakout_window=int(signal_breakout_window),
                exit_window=int(signal_exit_window)
            )

        st.session_state["latest_live_signal"] = signal_result

        st.subheader("Latest Signal Result")

        action = signal_result["action"]

        if action == "BUY":
            st.success("Signal Action: BUY")
        elif action == "SELL":
            st.warning("Signal Action: SELL")
        elif action == "HOLD":
            st.info("Signal Action: HOLD")
        else:
            st.info("Signal Action: STAY IN CASH")

        sig_metric1, sig_metric2, sig_metric3, sig_metric4 = st.columns(4)

        sig_metric1.metric("Ticker", signal_result["ticker"])
        sig_metric2.metric("Strategy", signal_result["strategy_label"])
        sig_metric3.metric("Latest Close", f"${signal_result['latest_close']:,.2f}")
        sig_metric4.metric("Latest Date", signal_result["latest_date"])

        st.write("Reason:", signal_result["reason"])

        with st.expander("Full Signal Details"):
            st.json(signal_result)

        st.subheader("Signal Strategy Summary")
        st.dataframe(signal_summary.round(2), use_container_width=True)

        log_audit_event(
            event_type="LIVE_SIGNAL_GENERATED",
            ticker=signal_result["ticker"],
            strategy_name=signal_result["strategy_label"],
            signal=signal_result["action"],
            broker_name="ibkr",
            execution_mode=EXECUTION_MODE,
            broker_status="not_submitted",
            message="Latest live broker signal generated from dashboard.",
            details=signal_result
        )

    except Exception as e:
        st.error("Could not generate latest signal.")
        st.exception(e)




# ==============================
# Signal to Order Proposal
# ==============================

st.markdown("---")
st.header("Signal to Order Proposal")
st.write(
    "Convert the latest generated signal into a proposed broker order for manual review. "
    "This does not submit the order."
)

latest_signal = st.session_state.get("latest_live_signal")

if not latest_signal:
    st.info("Generate a live broker signal first before creating an order proposal.")
else:
    st.subheader("Latest Signal Available")
    st.json(latest_signal)

    proposal_col1, proposal_col2, proposal_col3 = st.columns(3)

    with proposal_col1:
        proposal_account_equity = st.number_input(
            "Proposal Account Equity",
            min_value=1000.0,
            max_value=10000000.0,
            value=10000.0,
            step=1000.0,
            key="proposal_account_equity"
        )

    with proposal_col2:
        proposal_position_size = st.slider(
            "Proposal Position Size",
            min_value=0.001,
            max_value=0.10,
            value=0.01,
            step=0.001,
            key="proposal_position_size"
        )

    with proposal_col3:
        proposal_current_position_qty = st.number_input(
            "Current Position Quantity",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="proposal_current_position_qty"
        )

    proposal_col4, proposal_col5, proposal_col6 = st.columns(3)

    with proposal_col4:
        proposal_order_type = st.selectbox(
            "Proposal Order Type",
            ["LMT", "MKT"],
            index=0,
            key="proposal_order_type"
        )

    with proposal_col5:
        default_limit_price = float(latest_signal.get("latest_close", 1.0) or 1.0)

        proposal_limit_price = st.number_input(
            "Proposal Limit Price",
            min_value=0.0,
            value=default_limit_price,
            step=0.01,
            format="%.2f",
            key="proposal_limit_price"
        )

    with proposal_col6:
        proposal_allow_fractional = st.checkbox(
            "Allow Fractional Quantity",
            value=False,
            key="proposal_allow_fractional"
        )

    create_proposal_button = st.button(
        "Create Order Proposal from Signal",
        key="create_order_proposal_from_signal"
    )

    if create_proposal_button:
        try:
            order_proposal = build_order_proposal_from_signal(
                signal_result=latest_signal,
                account_equity=proposal_account_equity,
                position_size=proposal_position_size,
                order_type=proposal_order_type,
                limit_price=proposal_limit_price if proposal_order_type == "LMT" else None,
                allow_fractional=proposal_allow_fractional,
                current_position_quantity=proposal_current_position_qty,
                asset_type="etf" if latest_signal.get("ticker") in ["SPY", "QQQ"] else "stock",
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE
            )

            st.session_state["latest_order_proposal"] = order_proposal

            log_audit_event(
                event_type="ORDER_PROPOSAL_CREATED",
                ticker=order_proposal.get("ticker"),
                side=order_proposal.get("side"),
                quantity=order_proposal.get("quantity"),
                order_type=order_proposal.get("order_type"),
                limit_price=order_proposal.get("limit_price"),
                strategy_name=order_proposal.get("strategy_label"),
                signal=order_proposal.get("signal_action"),
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="not_submitted",
                message="Order proposal created from live signal.",
                details=order_proposal
            )

            if order_proposal.get("actionable"):
                st.success("Actionable order proposal created.")
            else:
                st.info("No actionable order was created from this signal.")

            st.json(order_proposal)

        except Exception as e:
            st.error("Could not create order proposal.")
            st.exception(e)

if "latest_order_proposal" in st.session_state:
    st.subheader("Latest Order Proposal")

    latest_order_proposal = st.session_state["latest_order_proposal"]

    if latest_order_proposal.get("actionable"):
        st.success("This proposal is actionable and ready for manual review.")
    else:
        st.info("This proposal is not actionable.")

    st.json(latest_order_proposal)

    if latest_order_proposal.get("actionable"):
        try:
            order_request = proposal_to_order_request(latest_order_proposal)

            st.subheader("Generated Order Request")
            st.json(order_request)

            st.info(
                "Next step: review this order request in the Broker Manual Approval Ticket. "
                "It will still require risk check and manual confirmation before submission."
            )

        except Exception as e:
            st.warning("Could not convert proposal into order request.")
            st.caption(str(e))










# ==============================
# Broker Account Snapshot
# ==============================

st.markdown("---")
st.header("Broker Account Snapshot")
st.write(
    "Capture a clean account snapshot from the current paper broker session. "
    "This helps the system understand cash, equity, open positions, and P&L before making decisions."
)

snapshot_button = st.button(
    "Capture Broker Account Snapshot",
    key="capture_broker_account_snapshot_button"
)

if snapshot_button:
    snapshot_result = get_broker_account_snapshot(
        paper_broker=st.session_state.get("paper_broker")
    )
    st.session_state["latest_broker_account_snapshot"] = snapshot_result

if "latest_broker_account_snapshot" in st.session_state:
    snapshot_result = st.session_state["latest_broker_account_snapshot"]
    snapshot_summary = get_snapshot_summary(snapshot_result)

    if snapshot_result.get("snapshot_available"):
        st.success("Broker account snapshot captured.")
    else:
        st.warning(snapshot_result.get("reason", "Snapshot unavailable."))

    snap_col1, snap_col2, snap_col3, snap_col4 = st.columns(4)

    snap_col1.metric("Cash", f"R {snapshot_summary.get('cash_balance', 0):,.2f}")
    snap_col2.metric("Equity", f"R {snapshot_summary.get('total_equity', 0):,.2f}")
    snap_col3.metric("Market Value", f"R {snapshot_summary.get('total_market_value', 0):,.2f}")
    snap_col4.metric("Positions", snapshot_summary.get("position_count", 0))

    snap_col5, snap_col6 = st.columns(2)

    snap_col5.metric("Unrealized P&L", f"R {snapshot_summary.get('total_unrealized_pnl', 0):,.2f}")
    snap_col6.metric("Environment", snapshot_summary.get("environment_status"))

    if snapshot_result.get("price_warnings"):
        st.warning(snapshot_result.get("price_warnings"))

    st.subheader("Snapshot Positions")

    positions_df = snapshot_positions_to_dataframe(snapshot_result)

    if positions_df.empty:
        st.info("No positions found in snapshot.")
    else:
        st.dataframe(positions_df, use_container_width=True)

    with st.expander("Full Snapshot JSON"):
        st.json(snapshot_result)
else:
    st.info("No broker account snapshot captured yet.")






# ==============================
# Fill and Slippage Tracking
# ==============================

st.markdown("---")
st.header("Fill and Slippage Tracking")
st.write(
    "Track order fills and compare fill prices against reference prices to monitor execution quality."
)

fill_status = get_fill_slippage_status()

fs_col1, fs_col2 = st.columns(2)

fs_col1.metric("Fill Count", fill_status.get("fill_count"))
fs_col2.metric("Checked At", fill_status.get("checked_at"))

st.subheader("Slippage Summary")

summary = fill_status.get("summary", {})

if summary.get("has_data"):
    ss_col1, ss_col2, ss_col3, ss_col4 = st.columns(4)

    ss_col1.metric("Total Fills", summary.get("fill_count"))
    ss_col2.metric("Total Quantity", f"{summary.get('total_fill_quantity', 0):,.2f}")

    avg_slip = summary.get("average_slippage_pct")
    worst_slip = summary.get("worst_slippage_pct")

    ss_col3.metric(
        "Avg Slippage",
        f"{avg_slip * 100:.4f}%" if avg_slip is not None else "N/A"
    )

    ss_col4.metric(
        "Worst Slippage",
        f"{worst_slip * 100:.4f}%" if worst_slip is not None else "N/A"
    )
else:
    st.info(summary.get("message", "No slippage summary available yet."))

st.subheader("Recent Fill Records")

fill_limit = st.number_input(
    "Fill Rows to View",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    key="fill_slippage_rows_to_view"
)

fills_df = read_order_fills(limit=fill_limit)

if fills_df.empty:
    st.info("No fill records found yet.")
else:
    st.dataframe(fills_df, use_container_width=True)

    fills_csv = fills_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Fill Records CSV",
        data=fills_csv,
        file_name="order_fills.csv",
        mime="text/csv",
        key="download_order_fills_csv"
    )

st.subheader("Manual Fill Record Test")

st.write(
    "Use this only for paper-trading review when you want to manually record a fill result."
)

mf_col1, mf_col2, mf_col3 = st.columns(3)

with mf_col1:
    manual_fill_ticker = st.selectbox(
        "Manual Fill Ticker",
        ["SPY", "QQQ", "AAPL", "MSFT"],
        key="manual_fill_ticker"
    )

with mf_col2:
    manual_fill_side = st.selectbox(
        "Manual Fill Side",
        ["BUY", "SELL"],
        key="manual_fill_side"
    )

with mf_col3:
    manual_fill_order_type = st.selectbox(
        "Manual Fill Order Type",
        ["LMT", "MKT"],
        key="manual_fill_order_type"
    )

mf_col4, mf_col5, mf_col6 = st.columns(3)

with mf_col4:
    manual_reference_price = st.number_input(
        "Manual Reference Price",
        min_value=0.0,
        value=500.00,
        step=0.01,
        format="%.2f",
        key="manual_fill_reference_price"
    )

with mf_col5:
    manual_fill_price = st.number_input(
        "Manual Fill Price",
        min_value=0.0,
        value=500.00,
        step=0.01,
        format="%.2f",
        key="manual_fill_price"
    )

with mf_col6:
    manual_fill_quantity = st.number_input(
        "Manual Fill Quantity",
        min_value=0.0,
        value=1.0,
        step=1.0,
        key="manual_fill_quantity"
    )

record_manual_fill_button = st.button(
    "Record Manual Fill",
    key="record_manual_fill_button"
)

if record_manual_fill_button:
    try:
        manual_fill_response = {
            "order_id": f"manual-fill-{manual_fill_ticker}-{manual_fill_side}",
            "ticker": manual_fill_ticker,
            "side": manual_fill_side,
            "order_type": manual_fill_order_type,
            "limit_price": manual_reference_price,
            "reference_price": manual_reference_price,
            "fill_price": manual_fill_price,
            "filled_quantity": manual_fill_quantity,
            "order_status": "filled_manual"
        }

        fill_result = record_fill_from_broker_response(
            broker_response=manual_fill_response,
            order_key=manual_fill_response["order_id"]
        )

        st.success("Manual fill recorded.")
        st.json(fill_result)

        log_audit_event(
            event_type="MANUAL_FILL_RECORDED",
            ticker=manual_fill_ticker,
            side=manual_fill_side,
            quantity=manual_fill_quantity,
            order_type=manual_fill_order_type,
            limit_price=manual_reference_price,
            broker_name="manual",
            execution_mode=EXECUTION_MODE,
            broker_status="filled_manual",
            message="Manual fill recorded for slippage tracking.",
            details=fill_result
        )

        st.rerun()

    except Exception as e:
        st.error("Could not record manual fill.")
        st.exception(e)


# ==============================
# Real Price Validation
# ==============================

st.markdown("---")
st.header("Real Price Validation")
st.write(
    "Validate proposed order prices against the latest available reference price before broker workflow."
)

price_validation_status = get_price_validation_status()

pv_col1, pv_col2 = st.columns(2)

pv_col1.metric(
    "Max BUY Premium",
    f"{price_validation_status.get('default_max_buy_premium_pct', 0) * 100:.1f}%"
)
pv_col2.metric(
    "Max SELL Discount",
    f"{price_validation_status.get('default_max_sell_discount_pct', 0) * 100:.1f}%"
)

with st.expander("Price Validation Rules"):
    for rule in price_validation_status.get("rules", []):
        st.write(f"- {rule}")

latest_proposal_for_price_check = st.session_state.get("latest_order_proposal")
latest_signal_for_price_check = st.session_state.get("latest_live_signal")
latest_snapshot_for_price_check = st.session_state.get("latest_broker_account_snapshot")

if not latest_proposal_for_price_check:
    st.info("No latest order proposal found. Create an order proposal first.")
else:
    st.subheader("Latest Proposal")
    st.json(latest_proposal_for_price_check)

    manual_reference_price = st.number_input(
        "Optional Manual Reference Price",
        min_value=0.0,
        value=0.0,
        step=0.01,
        format="%.2f",
        key="manual_reference_price_for_validation"
    )

    max_buy_premium = st.slider(
        "Max BUY Premium %",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.5,
        key="max_buy_premium_price_validation"
    ) / 100.0

    max_sell_discount = st.slider(
        "Max SELL Discount %",
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.5,
        key="max_sell_discount_price_validation"
    ) / 100.0

    run_price_validation_button = st.button(
        "Run Price Validation",
        key="run_price_validation_button"
    )

    if run_price_validation_button:
        try:
            price_validation_result = validate_order_price_from_proposal(
                proposal=latest_proposal_for_price_check,
                signal=latest_signal_for_price_check,
                account_snapshot=latest_snapshot_for_price_check,
                manual_reference_price=manual_reference_price if manual_reference_price > 0 else None,
                max_buy_premium_pct=max_buy_premium,
                max_sell_discount_pct=max_sell_discount
            )

            st.session_state["latest_price_validation_result"] = price_validation_result

            if price_validation_result.get("allowed"):
                st.success("Price validation passed.")
            else:
                st.error("Price validation blocked this proposal.")

            if price_validation_result.get("blockers"):
                st.error(price_validation_result.get("blockers"))

            if price_validation_result.get("warnings"):
                st.warning(price_validation_result.get("warnings"))

            with st.expander("Full Price Validation Result"):
                st.json(price_validation_result)

            log_audit_event(
                event_type="PRICE_VALIDATION_COMPLETED",
                ticker=price_validation_result.get("ticker"),
                side=price_validation_result.get("side"),
                order_type=price_validation_result.get("order_type"),
                limit_price=price_validation_result.get("limit_price"),
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="not_submitted",
                message="Price validation completed.",
                details=price_validation_result
            )

        except Exception as e:
            st.error("Price validation failed.")
            st.exception(e)


# ==============================
# Position-Aware Signal Execution
# ==============================

st.markdown("---")
st.header("Position-Aware Signal Execution")
st.write(
    "Check whether the latest order proposal makes sense against the current simulated paper positions."
)

position_status = get_position_aware_status()

pa_col1, pa_col2 = st.columns(2)

pa_col1.metric("Short Selling Default", str(position_status.get("short_selling_default")))
pa_col2.metric("Add to Existing Default", str(position_status.get("add_to_existing_default")))

with st.expander("Position-Aware Rules"):
    for rule in position_status.get("rules", []):
        st.write(f"- {rule}")

latest_proposal_for_position_check = st.session_state.get("latest_order_proposal")

if not latest_proposal_for_position_check:
    st.info("No latest order proposal found. Create an order proposal first.")
else:
    st.subheader("Latest Proposal")
    st.json(latest_proposal_for_position_check)

    latest_snapshot_for_position_check = st.session_state.get("latest_broker_account_snapshot")

    if latest_snapshot_for_position_check:
        st.info("Using latest Broker Account Snapshot for position-aware check.")
        current_paper_positions = latest_snapshot_for_position_check.get("positions", [])
    else:
        st.info("No Broker Account Snapshot found. Falling back to direct paper broker positions.")
        current_paper_positions = get_positions_from_paper_broker(
            st.session_state.get("paper_broker")
        )

    st.subheader("Current Paper Positions")

    if current_paper_positions:
        if isinstance(current_paper_positions, list):
            st.dataframe(pd.DataFrame(current_paper_positions), use_container_width=True)
        else:
            st.json(current_paper_positions)
    else:
        st.info("No current paper positions found.")

    allow_short_selling_pa = st.checkbox(
        "Allow short selling for this check",
        value=False,
        key="allow_short_selling_position_check"
    )

    allow_add_existing_pa = st.checkbox(
        "Allow adding to existing position for this check",
        value=False,
        key="allow_add_existing_position_check"
    )

    run_position_check_button = st.button(
        "Run Position-Aware Check",
        key="run_position_aware_check_button"
    )

    if run_position_check_button:
        try:
            if latest_snapshot_for_position_check:
                position_check_result = evaluate_position_aware_proposal_with_snapshot(
                    proposal=latest_proposal_for_position_check,
                    account_snapshot=latest_snapshot_for_position_check,
                    allow_short_selling=allow_short_selling_pa,
                    allow_add_to_existing=allow_add_existing_pa
                )
            else:
                position_check_result = evaluate_position_aware_proposal(
                    proposal=latest_proposal_for_position_check,
                    current_positions=current_paper_positions,
                    allow_short_selling=allow_short_selling_pa,
                    allow_add_to_existing=allow_add_existing_pa
                )

            st.session_state["latest_position_aware_check"] = position_check_result

            if position_check_result.get("allowed"):
                st.success("Position-aware check passed.")
            else:
                st.error("Position-aware check blocked this proposal.")

            if position_check_result.get("blockers"):
                st.error(position_check_result.get("blockers"))

            if position_check_result.get("warnings"):
                st.warning(position_check_result.get("warnings"))

            with st.expander("Full Position-Aware Check Result"):
                st.json(position_check_result)

            log_audit_event(
                event_type="POSITION_AWARE_CHECK_COMPLETED",
                ticker=position_check_result.get("ticker"),
                side=position_check_result.get("recommended_order_side"),
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="not_submitted",
                message="Position-aware check completed.",
                details=position_check_result
            )

        except Exception as e:
            st.error("Position-aware check failed.")
            st.exception(e)


# ==============================
# Duplicate Order Guard
# ==============================

st.markdown("---")
st.header("Duplicate Order Guard")
st.write(
    "Check whether a proposed order would duplicate an existing active order. "
    "This does not connect to IBKR or submit orders."
)

duplicate_status = get_duplicate_guard_status()

dup_col1, dup_col2 = st.columns(2)

dup_col1.metric("Active Order Count", duplicate_status.get("active_order_count"))
dup_col2.metric("Checked At", duplicate_status.get("checked_at"))

with st.expander("Duplicate Guard State Definitions"):
    st.write("Active states:")
    st.write(duplicate_status.get("active_order_states", []))
    st.write("Terminal states:")
    st.write(duplicate_status.get("terminal_order_states", []))

st.subheader("Active Orders by Ticker")

dup_ticker_filter = st.text_input(
    "Ticker Filter",
    value="",
    key="duplicate_guard_ticker_filter"
)

dup_side_filter = st.selectbox(
    "Side Filter",
    ["", "BUY", "SELL"],
    key="duplicate_guard_side_filter"
)

active_orders_df = get_active_orders_for_ticker(
    ticker=dup_ticker_filter.strip() or None,
    side=dup_side_filter or None
)

if active_orders_df.empty:
    st.info("No active orders found for the selected filter.")
else:
    st.dataframe(active_orders_df, use_container_width=True)

st.subheader("Check Latest Order Proposal for Duplicates")

latest_proposal_for_duplicate_check = st.session_state.get("latest_order_proposal")

if not latest_proposal_for_duplicate_check:
    st.info("No latest order proposal found. Create an order proposal first.")
else:
    st.json(latest_proposal_for_duplicate_check)

    duplicate_lookback_minutes = st.number_input(
        "Duplicate Lookback Minutes",
        min_value=5,
        max_value=10080,
        value=1440,
        step=5,
        key="duplicate_lookback_minutes"
    )

    run_duplicate_check_button = st.button(
        "Run Duplicate Check on Latest Proposal",
        key="run_duplicate_check_latest_proposal"
    )

    if run_duplicate_check_button:
        try:
            duplicate_result = check_duplicate_order_from_proposal(
                latest_proposal_for_duplicate_check,
                signal_id=None,
                lookback_minutes=duplicate_lookback_minutes
            )

            st.session_state["latest_duplicate_check"] = duplicate_result

            if duplicate_result.get("duplicate_blocked"):
                st.error("Duplicate order blocked.")
            else:
                st.success("No active duplicate blocker found.")

            if duplicate_result.get("warnings"):
                st.warning(duplicate_result.get("warnings"))

            with st.expander("Full Duplicate Check Result"):
                st.json(duplicate_result)

            log_audit_event(
                event_type="DUPLICATE_ORDER_CHECK_COMPLETED",
                ticker=duplicate_result.get("ticker"),
                side=duplicate_result.get("side"),
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="not_submitted",
                message="Duplicate order check completed.",
                details=duplicate_result
            )

        except Exception as e:
            st.error("Duplicate order check failed.")
            st.exception(e)


# ==============================
# Signal Review Page
# ==============================

st.markdown("---")
st.header("Signal Review Page")
st.write(
    "Review the latest generated signal, proposed order, emergency stop status, "
    "and risk readiness before any broker action."
)

review_signal = st.session_state.get("latest_live_signal")
review_proposal = st.session_state.get("latest_order_proposal")
review_emergency_state = read_emergency_stop_state()

if not review_signal:
    st.info("No signal has been generated yet. Please generate a live broker signal first.")
else:
    st.subheader("Latest Signal Review")

    signal_action = review_signal.get("action", "UNKNOWN")
    signal_ticker = review_signal.get("ticker", "N/A")
    signal_strategy = review_signal.get("strategy_label", "N/A")
    signal_latest_close = review_signal.get("latest_close", None)
    signal_latest_date = review_signal.get("latest_date", "N/A")
    signal_reason = review_signal.get("reason", "")

    sig_rev_col1, sig_rev_col2, sig_rev_col3, sig_rev_col4 = st.columns(4)

    sig_rev_col1.metric("Ticker", signal_ticker)
    sig_rev_col2.metric("Signal Action", signal_action)
    sig_rev_col3.metric("Strategy", signal_strategy)

    if signal_latest_close is not None:
        sig_rev_col4.metric("Latest Close", f"${float(signal_latest_close):,.2f}")
    else:
        sig_rev_col4.metric("Latest Close", "N/A")

    st.write("Latest Signal Date:", signal_latest_date)
    st.write("Signal Reason:", signal_reason)

    if signal_action == "BUY":
        st.success("Recommended signal action: BUY")
    elif signal_action == "SELL":
        st.warning("Recommended signal action: SELL")
    elif signal_action == "HOLD":
        st.info("Recommended signal action: HOLD existing position. No new entry order is required.")
    elif signal_action == "STAY IN CASH":
        st.info("Recommended signal action: stay out of the market. No order is required.")
    else:
        st.warning("Unknown signal action.")

    with st.expander("Full Signal Data"):
        st.json(review_signal)

st.subheader("Emergency Stop Review")

if review_emergency_state.get("active", False):
    st.error(
        f"Emergency stop is ACTIVE. Broker order submission must remain blocked. "
        f"Reason: {review_emergency_state.get('reason', '')}"
    )
else:
    st.success("Emergency stop is inactive.")

with st.expander("Emergency Stop State"):
    st.json(review_emergency_state)

st.subheader("Order Proposal Review")

if not review_proposal:
    st.info("No order proposal has been created yet. Create an order proposal from the latest signal first.")
else:
    proposal_actionable = review_proposal.get("actionable", False)
    proposal_status = review_proposal.get("proposal_status", "unknown")

    prop_col1, prop_col2, prop_col3, prop_col4 = st.columns(4)

    prop_col1.metric("Proposal Status", proposal_status)
    prop_col2.metric("Ticker", review_proposal.get("ticker", "N/A"))
    prop_col3.metric("Side", review_proposal.get("side", "N/A"))
    prop_col4.metric("Quantity", review_proposal.get("quantity", "N/A"))

    prop_col5, prop_col6, prop_col7, prop_col8 = st.columns(4)

    prop_col5.metric("Order Type", review_proposal.get("order_type", "N/A"))

    limit_price_value = review_proposal.get("limit_price")
    if limit_price_value is not None:
        prop_col6.metric("Limit Price", f"${float(limit_price_value):,.2f}")
    else:
        prop_col6.metric("Limit Price", "N/A")

    estimated_value = review_proposal.get("estimated_order_value")
    if estimated_value is not None:
        prop_col7.metric("Estimated Value", f"${float(estimated_value):,.2f}")
    else:
        prop_col7.metric("Estimated Value", "N/A")

    prop_col8.metric("Actionable", str(proposal_actionable))

    if proposal_actionable:
        st.success("This proposal is actionable and can move to risk review/manual broker ticket.")
    else:
        st.info(f"This proposal is not actionable. Reason: {review_proposal.get('reason', '')}")

    with st.expander("Full Order Proposal Data"):
        st.json(review_proposal)

st.subheader("Pre-Trade Recommendation")

if not review_signal:
    st.info("Step 1: Generate a live broker signal.")
elif not review_proposal:
    st.info("Step 2: Create an order proposal from the latest signal.")
elif review_emergency_state.get("active", False):
    st.error("Do not proceed. Emergency stop is active.")
elif not review_proposal.get("actionable", False):
    st.info("No broker order should be submitted because the current proposal is not actionable.")
else:
    st.success(
        "Signal and proposal are ready for manual broker review. "
        "Next: go to Broker Manual Approval Ticket, run risk check, tick manual confirmation, then submit paper order only if approved."
    )

    log_review_button = st.button(
        "Log Signal Review Decision",
        key="log_signal_review_decision"
    )

    if log_review_button:
        log_audit_event(
            event_type="SIGNAL_REVIEW_COMPLETED",
            ticker=review_proposal.get("ticker"),
            side=review_proposal.get("side"),
            quantity=review_proposal.get("quantity"),
            order_type=review_proposal.get("order_type"),
            limit_price=review_proposal.get("limit_price"),
            strategy_name=review_proposal.get("strategy_label"),
            signal=review_signal.get("action"),
            broker_name="ibkr",
            execution_mode=EXECUTION_MODE,
            broker_status="not_submitted",
            message="Signal review completed in dashboard.",
            details={
                "signal": review_signal,
                "proposal": review_proposal,
                "emergency_stop": review_emergency_state
            }
        )

        st.success("Signal review decision logged.")


# ==============================
# Broker Manual Approval Ticket
# ==============================

st.markdown("---")
st.header("Broker Manual Approval Ticket")
st.write(
    "Submit IBKR paper orders only after emergency-stop check, "
    "risk-manager approval, and manual confirmation."
)

st.warning(
    "This section is for IBKR PAPER trading only. "
    "Live trading remains disabled unless explicitly enabled later."
)


st.info(
    "Recommended workflow: Generate Signal → Create Order Proposal → Review Signal → "
    "Use latest proposal here → Run Risk Check → Tick confirmation → Submit IBKR Paper Order."
)



# Load latest actionable order proposal if available
latest_order_proposal_for_ticket = st.session_state.get("latest_order_proposal", {})

use_latest_proposal = False

if latest_order_proposal_for_ticket and latest_order_proposal_for_ticket.get("actionable", False):
    use_latest_proposal = st.checkbox(
        "Use latest actionable signal order proposal",
        value=True,
        key="use_latest_signal_order_proposal"
    )
else:
    st.info("No actionable signal order proposal is currently available for the broker ticket.")

ticket_emergency_state = read_emergency_stop_state()

if ticket_emergency_state.get("active", False):
    st.error(
        f"Emergency stop is ACTIVE. Broker orders are blocked. "
        f"Reason: {ticket_emergency_state.get('reason', '')}"
    )
else:
    st.success("Emergency stop is inactive.")

ticket_col1, ticket_col2, ticket_col3 = st.columns(3)

with ticket_col1:
    proposal_ticker_default = latest_order_proposal_for_ticket.get("ticker", "SPY") if use_latest_proposal else "SPY"
    ticker_options = ["SPY", "QQQ", "AAPL", "MSFT"]

    if proposal_ticker_default not in ticker_options:
        proposal_ticker_default = "SPY"

    broker_ticket_ticker = st.selectbox(
        "Broker Ticket Ticker",
        ticker_options,
        index=ticker_options.index(proposal_ticker_default),
        key="broker_ticket_ticker"
    )

with ticket_col2:
    proposal_side_default = latest_order_proposal_for_ticket.get("side", "BUY") if use_latest_proposal else "BUY"
    side_options = ["BUY", "SELL"]

    if proposal_side_default not in side_options:
        proposal_side_default = "BUY"

    broker_ticket_side = st.selectbox(
        "Side",
        side_options,
        index=side_options.index(proposal_side_default),
        key="broker_ticket_side"
    )

with ticket_col3:
    proposal_asset_default = latest_order_proposal_for_ticket.get("asset_type", "etf") if use_latest_proposal else "etf"
    asset_options = ["etf", "stock"]

    if proposal_asset_default not in asset_options:
        proposal_asset_default = "etf"

    broker_ticket_asset_type = st.selectbox(
        "Asset Type",
        asset_options,
        index=asset_options.index(proposal_asset_default),
        key="broker_ticket_asset_type"
    )

ticket_col4, ticket_col5, ticket_col6 = st.columns(3)

with ticket_col4:
    proposal_quantity_default = float(latest_order_proposal_for_ticket.get("quantity", 1.0)) if use_latest_proposal else 1.0

    broker_ticket_quantity = st.number_input(
        "Quantity",
        min_value=0.0,
        value=proposal_quantity_default,
        step=1.0,
        key="broker_ticket_quantity"
    )

with ticket_col5:
    proposal_order_type_default = latest_order_proposal_for_ticket.get("order_type", "LMT") if use_latest_proposal else "LMT"
    order_type_options = ["LMT", "MKT"]

    if proposal_order_type_default not in order_type_options:
        proposal_order_type_default = "LMT"

    broker_ticket_order_type = st.selectbox(
        "Order Type",
        order_type_options,
        index=order_type_options.index(proposal_order_type_default),
        key="broker_ticket_order_type"
    )

with ticket_col6:
    proposal_limit_default = latest_order_proposal_for_ticket.get("limit_price", 1.00) if use_latest_proposal else 1.00

    if proposal_limit_default is None:
        proposal_limit_default = 1.00

    broker_ticket_limit_price = st.number_input(
        "Limit Price",
        min_value=0.0,
        value=float(proposal_limit_default),
        step=0.01,
        format="%.2f",
        key="broker_ticket_limit_price"
    )

if broker_ticket_order_type == "MKT":
    st.info(
        "Market order selected. For safety, early broker testing should normally use limit orders."
    )

estimated_ticket_price = broker_ticket_limit_price if broker_ticket_order_type == "LMT" else 0.0
estimated_ticket_value = broker_ticket_quantity * estimated_ticket_price

st.subheader("Order Preview")

preview_col1, preview_col2, preview_col3, preview_col4 = st.columns(4)

preview_col1.metric("Ticker", broker_ticket_ticker)
preview_col2.metric("Side", broker_ticket_side)
preview_col3.metric("Quantity", f"{broker_ticket_quantity:,.2f}")
preview_col4.metric("Est. Order Value", f"${estimated_ticket_value:,.2f}")

manual_broker_confirmation = st.checkbox(
    "I confirm this is an IBKR PAPER order and I understand it may be submitted to the paper trading account.",
    key="manual_broker_confirmation"
)

run_ticket_risk_check = st.button(
    "Run Broker Risk Check",
    key="run_broker_ticket_risk_check"
)

if run_ticket_risk_check:
    risk_manager = create_risk_manager_from_config()

    # For now, this dashboard ticket does not yet calculate real broker position quantity.
    # We use 0 for BUY checks and 0 for SELL checks unless you manually update later.
    current_position_quantity = 0

    risk_result = risk_manager.approve_broker_order(
        ticker=broker_ticket_ticker,
        side=broker_ticket_side,
        quantity=broker_ticket_quantity,
        order_type=broker_ticket_order_type,
        asset_type=broker_ticket_asset_type,
        proposed_position_size=0.01,
        estimated_price=estimated_ticket_price if estimated_ticket_price > 0 else None,
        estimated_order_value=estimated_ticket_value if estimated_ticket_value > 0 else None,
        current_position_quantity=current_position_quantity,
        manual_confirmation_given=manual_broker_confirmation,
        broker_name="ibkr",
        execution_mode=EXECUTION_MODE,
        live_order=False
    )

    st.session_state["broker_ticket_risk_result"] = {
        "approved": risk_result.approved,
        "reason": risk_result.reason,
        "details": risk_result.details
    }

    log_audit_event(
        event_type="DASHBOARD_BROKER_RISK_CHECK",
        ticker=broker_ticket_ticker,
        side=broker_ticket_side,
        quantity=broker_ticket_quantity,
        order_type=broker_ticket_order_type,
        limit_price=broker_ticket_limit_price,
        risk_approved=risk_result.approved,
        risk_reason=risk_result.reason,
        manual_confirmation=manual_broker_confirmation,
        broker_name="ibkr",
        execution_mode=EXECUTION_MODE,
        broker_status="not_submitted",
        message="Dashboard broker ticket risk check completed.",
        details={
            **risk_result.details,
            "used_latest_signal_order_proposal": use_latest_proposal,
            "latest_order_proposal": latest_order_proposal_for_ticket if use_latest_proposal else {}
        }
    )

if "broker_ticket_risk_result" in st.session_state:
    risk_result_data = st.session_state["broker_ticket_risk_result"]

    st.subheader("Risk Check Result")

    if risk_result_data["approved"]:
        st.success(risk_result_data["reason"])
    else:
        st.error(risk_result_data["reason"])

    with st.expander("Risk Check Details"):
        st.json(risk_result_data["details"])

st.subheader("Submit IBKR Paper Order")

st.caption(
    "Submission is blocked unless risk check is approved, emergency stop is inactive, "
    "manual confirmation is checked, and IBKR paper order settings allow submission."
)

submit_broker_order = st.button(
    "Submit IBKR Paper Order",
    key="submit_ibkr_paper_order_button"
)

if submit_broker_order:
    risk_result_data = st.session_state.get("broker_ticket_risk_result")

    if ticket_emergency_state.get("active", False):
        st.error("Order blocked because emergency stop is active.")

        log_audit_event(
            event_type="DASHBOARD_ORDER_BLOCKED_EMERGENCY_STOP",
            ticker=broker_ticket_ticker,
            side=broker_ticket_side,
            quantity=broker_ticket_quantity,
            order_type=broker_ticket_order_type,
            limit_price=broker_ticket_limit_price,
            manual_confirmation=manual_broker_confirmation,
            broker_name="ibkr",
            execution_mode=EXECUTION_MODE,
            broker_status="blocked",
            message="Dashboard IBKR paper order blocked by emergency stop.",
            details=ticket_emergency_state
        )

    elif not manual_broker_confirmation:
        st.error("Order blocked because manual confirmation is not checked.")

        log_audit_event(
            event_type="DASHBOARD_ORDER_BLOCKED_NO_CONFIRMATION",
            ticker=broker_ticket_ticker,
            side=broker_ticket_side,
            quantity=broker_ticket_quantity,
            order_type=broker_ticket_order_type,
            limit_price=broker_ticket_limit_price,
            manual_confirmation=False,
            broker_name="ibkr",
            execution_mode=EXECUTION_MODE,
            broker_status="blocked",
            message="Dashboard IBKR paper order blocked because manual confirmation was missing."
        )

    elif not risk_result_data:
        st.error("Please run the Broker Risk Check before submitting.")

    elif not risk_result_data.get("approved", False):
        st.error("Order blocked because the risk check was not approved.")

        log_audit_event(
            event_type="DASHBOARD_ORDER_BLOCKED_RISK_CHECK",
            ticker=broker_ticket_ticker,
            side=broker_ticket_side,
            quantity=broker_ticket_quantity,
            order_type=broker_ticket_order_type,
            limit_price=broker_ticket_limit_price,
            risk_approved=False,
            risk_reason=risk_result_data.get("reason"),
            manual_confirmation=manual_broker_confirmation,
            broker_name="ibkr",
            execution_mode=EXECUTION_MODE,
            broker_status="blocked",
            message="Dashboard IBKR paper order blocked by risk check.",
            details=risk_result_data
        )


    else:
        duplicate_result = check_duplicate_order_from_proposal(
            {
                "ticker": broker_ticket_ticker,
                "side": broker_ticket_side,
                "quantity": broker_ticket_quantity,
                "order_type": broker_ticket_order_type,
                "limit_price": broker_ticket_limit_price,
                "actionable": True,
                "proposal_status": "manual_ticket",
                "strategy_label": "manual_broker_ticket"
            },
            signal_id=None,
            lookback_minutes=1440
        )

        if duplicate_result.get("duplicate_blocked"):
            st.error("Order blocked by Duplicate Order Guard.")
            st.json(duplicate_result)

            log_audit_event(
                event_type="DASHBOARD_ORDER_BLOCKED_DUPLICATE_GUARD",
                ticker=broker_ticket_ticker,
                side=broker_ticket_side,
                quantity=broker_ticket_quantity,
                order_type=broker_ticket_order_type,
                limit_price=broker_ticket_limit_price,
                risk_approved=True,
                manual_confirmation=manual_broker_confirmation,
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="blocked",
                message="Dashboard IBKR paper order blocked by duplicate order guard.",
                details=duplicate_result
            )


        latest_snapshot_for_manual_ticket = st.session_state.get("latest_broker_account_snapshot")

        manual_ticket_proposal_for_position_check = {
            "ticker": broker_ticket_ticker,
            "side": broker_ticket_side,
            "quantity": broker_ticket_quantity,
            "order_type": broker_ticket_order_type,
            "limit_price": broker_ticket_limit_price,
            "actionable": True,
            "proposal_status": "manual_ticket",
            "strategy_label": "manual_broker_ticket"
        }

        if latest_snapshot_for_manual_ticket:
            position_check_result = evaluate_position_aware_proposal_with_snapshot(
                proposal=manual_ticket_proposal_for_position_check,
                account_snapshot=latest_snapshot_for_manual_ticket,
                allow_short_selling=False,
                allow_add_to_existing=False
            )
        else:
            position_check_result = evaluate_position_aware_proposal(
                proposal=manual_ticket_proposal_for_position_check,
                current_positions=get_positions_from_paper_broker(
                    st.session_state.get("paper_broker")
                ),
                allow_short_selling=False,
                allow_add_to_existing=False
            )

        if not position_check_result.get("allowed"):
            st.error("Order blocked by Position-Aware Execution.")
            st.json(position_check_result)

            log_audit_event(
                event_type="DASHBOARD_ORDER_BLOCKED_POSITION_AWARE",
                ticker=broker_ticket_ticker,
                side=broker_ticket_side,
                quantity=broker_ticket_quantity,
                order_type=broker_ticket_order_type,
                limit_price=broker_ticket_limit_price,
                risk_approved=True,
                manual_confirmation=manual_broker_confirmation,
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="blocked",
                message="Dashboard IBKR paper order blocked by position-aware execution.",
                details=position_check_result
            )


        market_workflow_result = should_allow_market_order_workflow(
            market="US",
            allow_after_hours=False
        )

        if not market_workflow_result.get("allowed"):
            st.error("Order blocked by Market Hours Awareness.")
            st.json(market_workflow_result)

            log_audit_event(
                event_type="DASHBOARD_ORDER_BLOCKED_MARKET_HOURS",
                ticker=broker_ticket_ticker,
                side=broker_ticket_side,
                quantity=broker_ticket_quantity,
                order_type=broker_ticket_order_type,
                limit_price=broker_ticket_limit_price,
                risk_approved=True,
                manual_confirmation=manual_broker_confirmation,
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="blocked",
                message="Dashboard IBKR paper order blocked by market hours awareness.",
                details=market_workflow_result
            )


        latest_signal_for_manual_price_check = st.session_state.get("latest_live_signal")
        latest_snapshot_for_manual_price_check = st.session_state.get("latest_broker_account_snapshot")

        price_validation_result = validate_order_price_from_proposal(
            proposal={
                "ticker": broker_ticket_ticker,
                "side": broker_ticket_side,
                "quantity": broker_ticket_quantity,
                "order_type": broker_ticket_order_type,
                "limit_price": broker_ticket_limit_price,
                "actionable": True,
                "proposal_status": "manual_ticket",
                "strategy_label": "manual_broker_ticket"
            },
            signal=latest_signal_for_manual_price_check,
            account_snapshot=latest_snapshot_for_manual_price_check,
            manual_reference_price=None,
            max_buy_premium_pct=0.02,
            max_sell_discount_pct=0.02
        )

        if not price_validation_result.get("allowed"):
            st.error("Order blocked by Real Price Validation.")
            st.json(price_validation_result)

            log_audit_event(
                event_type="DASHBOARD_ORDER_BLOCKED_PRICE_VALIDATION",
                ticker=broker_ticket_ticker,
                side=broker_ticket_side,
                quantity=broker_ticket_quantity,
                order_type=broker_ticket_order_type,
                limit_price=broker_ticket_limit_price,
                risk_approved=True,
                manual_confirmation=manual_broker_confirmation,
                broker_name="ibkr",
                execution_mode=EXECUTION_MODE,
                broker_status="blocked",
                message="Dashboard IBKR paper order blocked by price validation.",
                details=price_validation_result
            )

        else:
            try:
                broker = get_broker("ibkr")

                if broker_ticket_order_type == "LMT":
                    broker_result = broker.submit_order(
                        ticker=broker_ticket_ticker,
                        side=broker_ticket_side,
                        quantity=broker_ticket_quantity,
                        order_type=broker_ticket_order_type,
                        limit_price=broker_ticket_limit_price
                    )
                else:
                    broker_result = broker.submit_order(
                        ticker=broker_ticket_ticker,
                        side=broker_ticket_side,
                        quantity=broker_ticket_quantity,
                        order_type=broker_ticket_order_type,
                        limit_price=None
                    )

                st.success("IBKR paper order submitted.")
                st.json(broker_result)

                try:
                    state_proposal = {
                        "ticker": broker_ticket_ticker,
                        "side": broker_ticket_side,
                        "quantity": broker_ticket_quantity,
                        "order_type": broker_ticket_order_type,
                        "limit_price": broker_ticket_limit_price,
                        "estimated_order_value": estimated_ticket_value,
                        "proposal_status": "manual_ticket_submitted",
                        "actionable": True,
                        "reason": "Paper order submitted from manual approval ticket."
                    }

                    state_create_result = create_order_state_from_proposal(
                        proposal=state_proposal,
                        proposal_id=None
                    )

                    record_broker_submission_state(
                        order_key=state_create_result["order_key"],
                        broker_response={
                            **broker_result,
                            "ticker": broker_ticket_ticker,
                            "side": broker_ticket_side,
                            "quantity": broker_ticket_quantity,
                            "order_type": broker_ticket_order_type,
                            "limit_price": broker_ticket_limit_price,
                            "execution_mode": EXECUTION_MODE,
                            "broker_name": "ibkr"
                        },
                        broker_order_row_id=None
                    )

                except Exception as state_error:
                    st.warning("Order submitted, but order state tracking failed.")
                    st.caption(str(state_error))

                try:
                    log_audit_event(
                        event_type="DASHBOARD_IBKR_PAPER_ORDER_SUBMITTED",
                        ticker=broker_ticket_ticker,
                        side=broker_ticket_side,
                        quantity=broker_ticket_quantity,
                        order_type=broker_ticket_order_type,
                        limit_price=broker_ticket_limit_price,
                        risk_approved=True,
                        manual_confirmation=manual_broker_confirmation,
                        broker_name="ibkr",
                        execution_mode=EXECUTION_MODE,
                        broker_status="submitted",
                        message="Dashboard IBKR paper order submitted from manual approval ticket.",
                        details={
                            "broker_result": broker_result,
                            "duplicate_guard": duplicate_result
                        }
                    )
                except Exception as audit_error:
                    st.warning("Order submitted, but audit logging failed.")
                    st.caption(str(audit_error))

            except Exception as e:
                st.error("IBKR paper order submission failed or was blocked.")
                st.exception(e)

            finally:
                try:
                    broker.disconnect()
                except Exception:
                    pass
# ==============================
# IBKR Paper Order Management
# ==============================

st.markdown("---")
st.header("IBKR Paper Order Management")
st.write(
    "View open IBKR paper orders and cancel selected open paper orders."
)

st.warning(
    "This section is for IBKR PAPER orders only. "
    "Live trading remains disabled."
)

refresh_open_orders = st.button(
    "Refresh IBKR Open Paper Orders",
    key="refresh_ibkr_open_orders"
)

if refresh_open_orders:
    try:
        broker = get_broker("ibkr")
        open_orders = broker.get_open_orders()

        st.session_state["ibkr_open_orders"] = open_orders

        try:
            broker.disconnect()
        except Exception:
            pass

        if open_orders:
            st.success(f"Found {len(open_orders)} open IBKR paper order(s).")
        else:
            st.info("No open IBKR paper orders found.")

    except Exception as e:
        st.error("Could not fetch IBKR open paper orders.")
        st.exception(e)

if "ibkr_open_orders" in st.session_state:
    open_orders = st.session_state["ibkr_open_orders"]

    if open_orders:
        open_orders_df = pd.DataFrame(open_orders)

        st.subheader("Open IBKR Paper Orders")
        st.dataframe(open_orders_df, use_container_width=True)

        available_order_ids = [
            int(order["order_id"])
            for order in open_orders
            if order.get("order_id") is not None
        ]

        if available_order_ids:
            selected_cancel_order_id = st.selectbox(
                "Select Order ID to Cancel",
                available_order_ids,
                key="selected_cancel_order_id"
            )

            cancel_confirmation = st.checkbox(
                "I confirm I want to cancel this IBKR PAPER order.",
                key="cancel_ibkr_order_confirmation"
            )

            cancel_button = st.button(
                "Cancel Selected IBKR Paper Order",
                key="cancel_selected_ibkr_paper_order"
            )

            if cancel_button:
                if not cancel_confirmation:
                    st.error("Please tick the cancellation confirmation checkbox first.")

                    log_audit_event(
                        event_type="DASHBOARD_CANCEL_BLOCKED_NO_CONFIRMATION",
                        order_id=selected_cancel_order_id,
                        broker_name="ibkr",
                        execution_mode=EXECUTION_MODE,
                        broker_status="blocked",
                        message="IBKR paper order cancellation blocked because confirmation was missing."
                    )

                else:
                    try:
                        broker = get_broker("ibkr")

                        cancel_result = broker.cancel_order(selected_cancel_order_id)

                        st.success("Cancel request sent to IBKR paper account.")
                        st.json(cancel_result)

                        log_audit_event(
                            event_type="DASHBOARD_IBKR_PAPER_ORDER_CANCEL_REQUESTED",
                            order_id=selected_cancel_order_id,
                            broker_name="ibkr",
                            execution_mode=EXECUTION_MODE,
                            broker_status="cancel_requested",
                            message="Dashboard cancel request sent for IBKR paper order.",
                            details=cancel_result
                        )

                        updated_open_orders = broker.get_open_orders()
                        st.session_state["ibkr_open_orders"] = updated_open_orders

                        try:
                            broker.disconnect()
                        except Exception:
                            pass

                        st.rerun()

                    except Exception as e:
                        st.error("IBKR paper order cancellation failed or was blocked.")
                        st.exception(e)

                        log_audit_event(
                            event_type="DASHBOARD_IBKR_PAPER_ORDER_CANCEL_FAILED",
                            order_id=selected_cancel_order_id,
                            broker_name="ibkr",
                            execution_mode=EXECUTION_MODE,
                            broker_status="failed",
                            message="Dashboard IBKR paper order cancellation failed.",
                            error=e
                        )
        else:
            st.info("No valid order IDs found in open orders.")
    else:
        st.info("No open IBKR paper orders found.")








# ==============================
# Secure Broker Architecture Plan
# ==============================

st.markdown("---")
st.header("Secure Broker Architecture Plan")
st.write(
    "Review the current broker architecture stage, allowed environments, prohibited actions, "
    "and remaining components before any future live trading consideration."
)

architecture_status = get_secure_broker_architecture_status()

arch_col1, arch_col2, arch_col3 = st.columns(3)

arch_col1.metric("Current Stage", architecture_status.get("current_stage"))
arch_col2.metric("Live Trading Status", architecture_status.get("live_trading_status"))
arch_col3.metric("Checked At", architecture_status.get("timestamp"))

st.info(architecture_status.get("recommendation"))

st.subheader("Recommended Use Right Now")
st.success(architecture_status.get("recommended_use_now"))

st.subheader("Architecture Modes")

architecture_modes_df = pd.DataFrame(architecture_status.get("architecture_modes", []))

if not architecture_modes_df.empty:
    st.dataframe(architecture_modes_df, use_container_width=True)

st.subheader("Required Next Components")

for item in architecture_status.get("required_next_components", []):
    st.write(f"- {item}")

st.subheader("Currently Prohibited")

for item in architecture_status.get("prohibited_currently", []):
    st.warning(item)

with st.expander("Full Architecture Status"):
    st.json(architecture_status)


# ==============================
# Deployment Health Check
# ==============================

st.markdown("---")
st.header("Deployment Health Check")
st.write(
    "Check whether the app is running locally or on Streamlit Cloud, "
    "and confirm which features are available in the current environment."
)

run_deployment_health_button = st.button(
    "Run Deployment Health Check",
    key="run_deployment_health_check_button"
)

if run_deployment_health_button:
    deployment_health_result = run_deployment_health_check()
    st.session_state["latest_deployment_health_check"] = deployment_health_result

if "latest_deployment_health_check" in st.session_state:
    deployment_health_result = st.session_state["latest_deployment_health_check"]

    dep_col1, dep_col2, dep_col3 = st.columns(3)

    dep_col1.metric("Deployment Status", deployment_health_result.get("status"))
    dep_col2.metric(
        "Environment",
        deployment_health_result.get("runtime", {}).get("environment")
    )
    dep_col3.metric("Checked At", deployment_health_result.get("timestamp"))

    st.info(deployment_health_result.get("recommendation"))

    st.subheader("Runtime Details")
    with st.expander("Runtime Snapshot"):
        st.json(deployment_health_result.get("runtime", {}))

    st.subheader("IBKR Localhost Availability")

    localhost_df = pd.DataFrame(deployment_health_result.get("localhost_ibkr", []))

    if not localhost_df.empty:
        st.dataframe(localhost_df, use_container_width=True)

        reachable_rows = localhost_df[localhost_df["reachable"] == True]

        if reachable_rows.empty:
            st.warning(
                "No IBKR localhost ports are reachable from this runtime. "
                "This is normal on Streamlit Cloud and normal locally if TWS/IB Gateway is closed."
            )
        else:
            st.success("At least one IBKR localhost port appears reachable.")
    else:
        st.info("No localhost check results available.")

    st.subheader("Feature Availability Matrix")

    feature_df = pd.DataFrame(deployment_health_result.get("feature_matrix", []))

    if not feature_df.empty:
        st.dataframe(feature_df, use_container_width=True)

        unavailable = feature_df[feature_df["available"] == False]

        if not unavailable.empty:
            st.warning("Some features are unavailable in this runtime. Review notes below.")
            st.dataframe(unavailable, use_container_width=True)
    else:
        st.info("No feature matrix available.")

    st.download_button(
        label="Download Deployment Health Check",
        data=str(deployment_health_result),
        file_name="deployment_health_check.txt",
        mime="text/plain",
        key="download_deployment_health_check"
    )






# ==============================
# Unified Order State Manager
# ==============================

st.markdown("---")
st.header("Unified Order State Manager")
st.write(
    "Track the lifecycle state of proposed, approved, submitted, filled, cancelled, rejected, and failed orders."
)

init_order_state_button = st.button(
    "Initialize Order State Tables",
    key="initialize_order_state_tables_button"
)

if init_order_state_button:
    initialize_order_state_tables()
    st.success("Order state tables initialized.")

order_state_status = get_order_state_manager_status()

state_col1, state_col2 = st.columns(2)

state_col1.metric("Current Orders", order_state_status.get("current_orders"))
state_col2.metric("State Events", order_state_status.get("state_events"))

with st.expander("Valid Order States"):
    st.write(order_state_status.get("valid_states", []))

with st.expander("Terminal Order States"):
    st.write(order_state_status.get("terminal_states", []))

st.subheader("Current Order States")

current_state_limit = st.number_input(
    "Current State Rows",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    key="current_order_state_limit"
)

current_states_df = read_order_current_states(limit=current_state_limit)

if current_states_df.empty:
    st.info("No current order states found yet.")
else:
    st.dataframe(current_states_df, use_container_width=True)

st.subheader("Order State Events")

event_state_limit = st.number_input(
    "State Event Rows",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    key="order_state_event_limit"
)

order_key_filter = st.text_input(
    "Optional Order Key Filter",
    value="",
    key="order_key_filter"
)

if order_key_filter.strip():
    events_df = read_order_state_events(order_key=order_key_filter.strip(), limit=event_state_limit)
else:
    events_df = read_order_state_events(limit=event_state_limit)

if events_df.empty:
    st.info("No order state events found yet.")
else:
    st.dataframe(events_df, use_container_width=True)

    csv_data = events_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Order State Events CSV",
        data=csv_data,
        file_name="order_state_events.csv",
        mime="text/csv",
        key="download_order_state_events_csv"
    )


# ==============================
# SQLite Trading Database
# ==============================

st.markdown("---")
st.header("SQLite Trading Database")
st.write(
    "Review the local SQLite database foundation for signals, proposals, risk checks, "
    "broker orders, audit events, and system events."
)

init_db_button = st.button(
    "Initialize Trading Database",
    key="initialize_trading_database_button"
)

if init_db_button:
    db_file = sqlite_initialize_trading_database()
    st.success("Trading database initialized.")
    st.caption(db_file)

db_status = sqlite_get_database_status()

db_col1, db_col2 = st.columns(2)

db_col1.metric("Database Exists", str(db_status.get("database_exists")))
db_col2.metric("Database File", db_status.get("database_file"))

st.subheader("Database Tables")

tables_df = pd.DataFrame(db_status.get("tables", []))

if not tables_df.empty:
    st.dataframe(tables_df, use_container_width=True)
else:
    st.info("No database table status available.")

st.subheader("View Database Table")

table_to_view = st.selectbox(
    "Select Table",
    [
        "signals",
        "order_proposals",
        "risk_checks",
        "broker_orders",
        "audit_events",
        "system_events",
        "order_state_events",
        "order_current_state",
        "order_fills",
        "slippage_summary",
        "error_notifications",
        "test_run_results",
    ],
    key="database_table_to_view"
)

table_limit = st.number_input(
    "Rows to View",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    key="database_table_limit"
)

view_table_button = st.button(
    "View Selected Database Table",
    key="view_selected_database_table"
)

if view_table_button:
    try:
        table_df = sqlite_read_table(table_to_view, limit=table_limit)

        if table_df.empty:
            st.info(f"No rows found in {table_to_view}.")
        else:
            st.dataframe(table_df, use_container_width=True)

            csv_data = table_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label=f"Download {table_to_view} CSV",
                data=csv_data,
                file_name=f"{table_to_view}.csv",
                mime="text/csv",
                key=f"download_{table_to_view}_csv"
            )

    except Exception as e:
        st.error("Could not read database table.")
        st.exception(e)






# ==============================
# Automated Test Runner
# ==============================

st.markdown("---")
st.header("Automated Test Runner")
st.write(
    "Run selected safe local test scripts and review pass/fail results. "
    "Broker connection tests are excluded by default."
)

test_runner_status = get_test_runner_status()
test_summary = test_runner_status.get("summary", {})

tr_col1, tr_col2, tr_col3, tr_col4 = st.columns(4)

tr_col1.metric("Safe Tests", test_runner_status.get("safe_tests_count"))
tr_col2.metric("Latest Unique Tests", test_summary.get("latest_unique_tests", 0))
tr_col3.metric("Latest Passed", test_summary.get("latest_passed", 0))
tr_col4.metric(
    "Latest Pass Rate",
    f"{test_summary.get('latest_pass_rate', 0) * 100:.1f}%"
)

if test_summary.get("latest_failed", 0) > 0:
    st.warning("Some latest test results failed. Review before broker testing.")
elif test_summary.get("has_data"):
    st.success("Latest recorded tests are passing.")
else:
    st.info("No test results recorded yet.")

st.warning(
    "Note: test_failure_notification_dummy.py is intentionally designed to fail. "
    "Use it only when testing error notification integration."
)

st.subheader("Available Safe Tests")

available_tests = test_runner_status.get("available_safe_tests", [])
available_df = pd.DataFrame(available_tests)

if not available_df.empty:
    st.dataframe(available_df, use_container_width=True)

existing_safe_tests = [
    row["test_script"]
    for row in available_tests
    if row.get("exists")
]

selected_tests = st.multiselect(
    "Select Safe Tests to Run",
    options=existing_safe_tests,
    default=[],
    key="selected_safe_tests_to_run"
)

test_timeout = st.number_input(
    "Timeout per Test Script Seconds",
    min_value=30,
    max_value=600,
    value=120,
    step=30,
    key="test_runner_timeout_seconds"
)

run_selected_tests_button = st.button(
    "Run Selected Tests",
    key="run_selected_tests_button"
)

if run_selected_tests_button:
    if not selected_tests:
        st.error("Please select at least one test script.")
    else:
        with st.spinner("Running selected tests..."):
            results = run_selected_tests(
                test_scripts=selected_tests,
                timeout_seconds=test_timeout
            )

        st.session_state["latest_test_runner_results"] = results

        passed_count = sum(1 for result in results if result.get("passed"))
        failed_count = len(results) - passed_count

        if failed_count == 0:
            st.success(f"All selected tests passed: {passed_count}/{len(results)}")
        else:
            st.error(f"Some tests failed: {failed_count}/{len(results)}")

run_safe_suite_button = st.button(
    "Run Full Safe Test Suite",
    key="run_full_safe_test_suite_button"
)

if run_safe_suite_button:
    with st.spinner("Running full safe test suite..."):
        results = run_safe_test_suite(timeout_seconds=test_timeout)

    st.session_state["latest_test_runner_results"] = results

    passed_count = sum(1 for result in results if result.get("passed"))
    failed_count = len(results) - passed_count

    if failed_count == 0:
        st.success(f"Full safe test suite passed: {passed_count}/{len(results)}")
    else:
        st.error(f"Some safe tests failed: {failed_count}/{len(results)}")

if "latest_test_runner_results" in st.session_state:
    st.subheader("Latest Test Runner Output")

    latest_results = st.session_state["latest_test_runner_results"]

    results_df = pd.DataFrame([
        {
            "test_script": result.get("test_script"),
            "passed": result.get("passed"),
            "return_code": result.get("return_code"),
            "duration_seconds": result.get("duration_seconds"),
            "stderr_preview": str(result.get("stderr_text", ""))[:300],
        }
        for result in latest_results
    ])

    st.dataframe(results_df, use_container_width=True)

    with st.expander("Full Latest Test Outputs"):
        st.json(latest_results)

st.subheader("Recent Saved Test Results")

test_result_limit = st.number_input(
    "Saved Test Results to View",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    key="saved_test_results_limit"
)

saved_results_df = read_test_results(limit=test_result_limit)

if saved_results_df.empty:
    st.info("No saved test results found.")
else:
    st.dataframe(saved_results_df, use_container_width=True)

    test_csv = saved_results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Test Results CSV",
        data=test_csv,
        file_name="test_run_results.csv",
        mime="text/csv",
        key="download_test_run_results_csv"
    )


# ==============================
# Error Notification System
# ==============================

st.markdown("---")
st.header("Error Notification System")
st.write(
    "Review system errors, warnings, critical events, and resolved notifications."
)

error_status = get_error_notifier_status()
error_summary = error_status.get("summary", {})

err_col1, err_col2, err_col3, err_col4 = st.columns(4)

err_col1.metric("Total Notifications", error_summary.get("total_errors", 0))
err_col2.metric("Unresolved", error_summary.get("unresolved_errors", 0))
err_col3.metric("Critical", error_summary.get("critical_errors", 0))
err_col4.metric("Checked At", error_status.get("checked_at"))

if error_summary.get("critical_errors", 0) > 0:
    st.error("Critical notifications exist. Review before broker testing.")
elif error_summary.get("unresolved_errors", 0) > 0:
    st.warning("Unresolved notifications exist. Review before continuing.")
else:
    st.success("No unresolved error notifications found.")

with st.expander("Error Summary"):
    st.json(error_summary)

st.subheader("Create Manual Notification")

manual_err_col1, manual_err_col2 = st.columns(2)

with manual_err_col1:
    manual_notification_component = st.text_input(
        "Component",
        value="manual_dashboard_note",
        key="manual_notification_component"
    )

with manual_err_col2:
    manual_notification_severity = st.selectbox(
        "Severity",
        ["INFO", "WARNING", "ERROR", "CRITICAL"],
        key="manual_notification_severity"
    )

manual_notification_message = st.text_area(
    "Notification Message",
    value="",
    key="manual_notification_message"
)

create_manual_notification_button = st.button(
    "Create Manual Notification",
    key="create_manual_notification_button"
)

if create_manual_notification_button:
    if not manual_notification_message.strip():
        st.error("Notification message cannot be empty.")
    else:
        result = notify_message(
            component=manual_notification_component,
            message=manual_notification_message,
            severity=manual_notification_severity,
            context={"source": "streamlit_dashboard"}
        )

        st.success("Manual notification recorded.")
        st.json(result)
        st.rerun()

st.subheader("Notification Records")

unresolved_only = st.checkbox(
    "Show unresolved only",
    value=False,
    key="show_unresolved_notifications_only"
)

severity_filter = st.selectbox(
    "Severity Filter",
    ["", "INFO", "WARNING", "ERROR", "CRITICAL"],
    key="error_notification_severity_filter"
)

notification_limit = st.number_input(
    "Notifications to View",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    key="error_notification_limit"
)

notifications_df = read_error_notifications(
    limit=notification_limit,
    unresolved_only=unresolved_only,
    severity=severity_filter if severity_filter else None
)

if notifications_df.empty:
    st.info("No notifications found for selected filters.")
else:
    st.dataframe(notifications_df, use_container_width=True)

    csv_data = notifications_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Error Notifications CSV",
        data=csv_data,
        file_name="error_notifications.csv",
        mime="text/csv",
        key="download_error_notifications_csv"
    )

st.subheader("Mark Notification as Resolved")

resolve_error_id = st.number_input(
    "Notification ID to Resolve",
    min_value=1,
    value=1,
    step=1,
    key="resolve_error_notification_id"
)

resolution_note = st.text_area(
    "Resolution Note",
    value="Resolved after review.",
    key="resolution_note"
)

resolve_notification_button = st.button(
    "Mark Notification Resolved",
    key="mark_notification_resolved_button"
)

if resolve_notification_button:
    resolve_result = mark_error_resolved(
        error_id=resolve_error_id,
        resolution_note=resolution_note
    )

    if resolve_result.get("updated"):
        st.success("Notification marked as resolved.")
        st.json(resolve_result)
        st.rerun()
    else:
        st.warning("No notification was updated. Check the notification ID.")


# ==============================
# System Health Check Dashboard
# ==============================

st.markdown("---")
st.header("System Health Check Dashboard")
st.write(
    "Run a full diagnostic check of project files, imports, safety systems, config, and logs. "
    "This does not connect to IBKR or place orders."
)

run_health_check_button = st.button(
    "Run System Health Check",
    key="run_system_health_check_button"
)

if run_health_check_button:
    health_result = run_system_health_check()
    st.session_state["latest_system_health_check"] = health_result

if "latest_system_health_check" in st.session_state:
    health_result = st.session_state["latest_system_health_check"]

    health_col1, health_col2, health_col3 = st.columns(3)

    health_col1.metric("Health Status", health_result.get("status"))
    health_col2.metric("Overall OK", str(health_result.get("overall_ok")))
    health_col3.metric("Checked At", health_result.get("timestamp"))

    if health_result.get("overall_ok"):
        st.success(health_result.get("recommendation"))
    elif health_result.get("status") == "warning":
        st.warning(health_result.get("recommendation"))
    else:
        st.error(health_result.get("recommendation"))

    st.subheader("Health Summary")
    st.json(health_result.get("summary", {}))

    st.subheader("Required Files")
    st.dataframe(pd.DataFrame(health_result.get("files", [])), use_container_width=True)

    st.subheader("Required Folders")
    st.dataframe(pd.DataFrame(health_result.get("folders", [])), use_container_width=True)

    st.subheader("Module Import Checks")
    module_df = pd.DataFrame(health_result.get("modules", []))

    if not module_df.empty:
        st.dataframe(module_df, use_container_width=True)

        failed_modules = module_df[module_df["import_ok"] == False]

        if not failed_modules.empty:
            st.error("Some modules failed to import.")
            st.dataframe(failed_modules, use_container_width=True)
    else:
        st.info("No module check results found.")

    st.subheader("Config Safety")
    config_safety = health_result.get("config_safety", {})

    if config_safety.get("ok"):
        st.success("Config safety check passed.")
    else:
        st.error("Config safety check has blockers.")

    with st.expander("Config Safety Details"):
        st.json(config_safety)

    st.subheader("Safety Systems")
    safety_systems = health_result.get("safety_systems", {})

    safety_rows = []

    for system_name, system_result in safety_systems.items():
        safety_rows.append({
            "system": system_name,
            "ok": system_result.get("ok", False),
            "error": system_result.get("error", "")
        })

    st.dataframe(pd.DataFrame(safety_rows), use_container_width=True)

    with st.expander("Full Safety System Details"):
        st.json(safety_systems)

    st.subheader("Local Logs")
    st.dataframe(pd.DataFrame(health_result.get("logs", [])), use_container_width=True)

    st.download_button(
        label="Download System Health Check JSON",
        data=str(health_result),
        file_name="system_health_check.txt",
        mime="text/plain",
        key="download_system_health_check"
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
p_col4.metric("Open Positions", len(portfolio_account.get("open_positions", [])))

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
    db_status = sqlite_get_database_status()

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
