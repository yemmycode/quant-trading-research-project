
import pandas as pd
import numpy as np
import yfinance as yf


def calculate_rsi(price_series, rsi_window=14):
    """
    Calculate Relative Strength Index.
    """

    price_change = price_series.diff()

    gains = price_change.where(price_change > 0, 0)
    losses = -price_change.where(price_change < 0, 0)

    average_gain = gains.rolling(window=rsi_window).mean()
    average_loss = losses.rolling(window=rsi_window).mean()

    relative_strength = average_gain / average_loss

    rsi = 100 - (100 / (1 + relative_strength))

    return rsi


def calculate_performance_metrics(
    data,
    return_column,
    growth_column,
    drawdown_column,
    initial_capital=10000
):
    """
    Calculate professional strategy performance metrics.
    """

    total_return = data[growth_column].iloc[-1] - 1
    volatility = data[return_column].std() * np.sqrt(252)

    annual_return = data[return_column].mean() * 252

    sharpe_ratio = (
        annual_return / volatility
        if volatility != 0 else np.nan
    )

    downside_returns = data.loc[data[return_column] < 0, return_column]
    downside_volatility = downside_returns.std() * np.sqrt(252)

    sortino_ratio = (
        annual_return / downside_volatility
        if downside_volatility != 0 else np.nan
    )

    max_drawdown = data[drawdown_column].min()

    calmar_ratio = (
        annual_return / abs(max_drawdown)
        if max_drawdown != 0 else np.nan
    )

    positive_returns = data.loc[data[return_column] > 0, return_column]
    negative_returns = data.loc[data[return_column] < 0, return_column]

    win_rate = (
        len(positive_returns) / (len(positive_returns) + len(negative_returns))
        if (len(positive_returns) + len(negative_returns)) > 0 else np.nan
    )

    average_win = positive_returns.mean() if len(positive_returns) > 0 else np.nan
    average_loss = negative_returns.mean() if len(negative_returns) > 0 else np.nan

    total_gains = positive_returns.sum()
    total_losses = abs(negative_returns.sum())

    profit_factor = (
        total_gains / total_losses
        if total_losses != 0 else np.nan
    )

    recovery_factor = (
        total_return / abs(max_drawdown)
        if max_drawdown != 0 else np.nan
    )

    final_value = initial_capital * data[growth_column].iloc[-1]

    return {
        "Total Return (%)": total_return * 100,
        "Annual Return (%)": annual_return * 100,
        "Volatility (%)": volatility * 100,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Calmar Ratio": calmar_ratio,
        "Max Drawdown (%)": max_drawdown * 100,
        "Win Rate (%)": win_rate * 100,
        "Average Win (%)": average_win * 100 if not pd.isna(average_win) else np.nan,
        "Average Loss (%)": average_loss * 100 if not pd.isna(average_loss) else np.nan,
        "Profit Factor": profit_factor,
        "Recovery Factor": recovery_factor,
        "Final Value (R)": final_value
    }




def generate_trade_log(data):
    """
    Generate detailed trade log from strategy positions.
    """

    trades = []

    in_trade = False
    entry_date = None
    entry_price = None

    for current_date, row in data.iterrows():

        position = row["Position"]
        close_price = row["Close"]

        # Entry
        if not in_trade and position == 1:
            in_trade = True
            entry_date = current_date
            entry_price = close_price

        # Exit
        elif in_trade and position == 0:
            exit_date = current_date
            exit_price = close_price

            trade_return = (
                (exit_price - entry_price) / entry_price
            ) * 100

            holding_days = (exit_date - entry_date).days

            trades.append({
                "Entry Date": entry_date,
                "Exit Date": exit_date,
                "Entry Price": entry_price,
                "Exit Price": exit_price,
                "Holding Days": holding_days,
                "Trade Return (%)": trade_return,
                "Win/Loss": "Win" if trade_return > 0 else "Loss"
            })

            in_trade = False

    trade_log = pd.DataFrame(trades)

    return trade_log


def run_rsi_backtest(
    ticker="SPY",
    start_date="2018-01-01",
    end_date="2025-01-01",
    rsi_window=14,
    oversold_level=30,
    overbought_level=70,
    regime_window=200,
    position_size=0.50,
    trading_cost=0.001,
    initial_capital=10000
):
    """
    Run an RSI strategy backtest with:
    - RSI oversold/overbought rules
    - 200-day market regime filter
    - transaction cost adjustment
    - position sizing
    - professional performance metrics
    """

    raw_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if raw_data.empty:
        raise ValueError(f"No data downloaded for ticker: {ticker}")

    if isinstance(raw_data.columns, pd.MultiIndex):
        close_series = raw_data["Close"]
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]
    else:
        close_series = raw_data["Close"]

    data = pd.DataFrame()
    data["Close"] = close_series.astype(float)
    data.dropna(inplace=True)

    data["Daily_Return"] = data["Close"].pct_change()

    data["RSI"] = calculate_rsi(data["Close"], rsi_window=rsi_window)
    data["MA_Regime"] = data["Close"].rolling(window=regime_window).mean()
    data["Market_Regime"] = np.where(data["Close"] > data["MA_Regime"], 1, 0)

    data["Signal"] = 0

    data.loc[
        (data["RSI"] < oversold_level) & (data["Market_Regime"] == 1),
        "Signal"
    ] = 1

    data["Signal"] = data["Signal"].replace(0, np.nan).ffill().fillna(0)

    data.loc[
        (data["RSI"] > overbought_level) | (data["Market_Regime"] == 0),
        "Signal"
    ] = 0

    data["Signal"] = data["Signal"].ffill().fillna(0)

    data["Position"] = data["Signal"].shift(1)

    data["Strategy_Return"] = data["Position"] * data["Daily_Return"]

    data["Trade_Event"] = data["Position"].diff().abs().fillna(0)

    data["Strategy_Return_After_Cost"] = (
        data["Strategy_Return"] - (data["Trade_Event"] * trading_cost)
    )

    data["Strategy_Return_Final"] = data["Strategy_Return_After_Cost"] * position_size

    data.dropna(inplace=True)

    if data.empty:
        raise ValueError(
            "Not enough data after calculations. Try a longer date range."
        )

    data["Buy_Hold_Growth"] = (1 + data["Daily_Return"]).cumprod()
    data["Strategy_Growth"] = (1 + data["Strategy_Return_Final"]).cumprod()

    data["Buy_Hold_Peak"] = data["Buy_Hold_Growth"].cummax()
    data["Strategy_Peak"] = data["Strategy_Growth"].cummax()

    data["Buy_Hold_Drawdown"] = (
        data["Buy_Hold_Growth"] - data["Buy_Hold_Peak"]
    ) / data["Buy_Hold_Peak"]

    data["Strategy_Drawdown"] = (
        data["Strategy_Growth"] - data["Strategy_Peak"]
    ) / data["Strategy_Peak"]

    buy_hold_metrics = calculate_performance_metrics(
        data=data,
        return_column="Daily_Return",
        growth_column="Buy_Hold_Growth",
        drawdown_column="Buy_Hold_Drawdown",
        initial_capital=initial_capital
    )

    strategy_metrics = calculate_performance_metrics(
        data=data,
        return_column="Strategy_Return_Final",
        growth_column="Strategy_Growth",
        drawdown_column="Strategy_Drawdown",
        initial_capital=initial_capital
    )

    data["Trade"] = data["Signal"].diff()
    buy_trades = (data["Trade"] == 1).sum()
    sell_trades = (data["Trade"] == -1).sum()

    summary = pd.DataFrame([
        {
            "Strategy": "Buy and Hold",
            "Ticker": ticker,
            "RSI Window": np.nan,
            "Oversold Level": np.nan,
            "Overbought Level": np.nan,
            "Regime Window": np.nan,
            "Position Size": 1.0,
            "Trading Cost": 0.0,
            **buy_hold_metrics,
            "Buy Trades": np.nan,
            "Sell Trades": np.nan
        },
        {
            "Strategy": "RSI Strategy",
            "Ticker": ticker,
            "RSI Window": rsi_window,
            "Oversold Level": oversold_level,
            "Overbought Level": overbought_level,
            "Regime Window": regime_window,
            "Position Size": position_size,
            "Trading Cost": trading_cost,
            **strategy_metrics,
            "Buy Trades": buy_trades,
            "Sell Trades": sell_trades
        }
    ])


    trade_log = generate_trade_log(data)

    return data, summary, trade_log

