
import pandas as pd
import numpy as np
import yfinance as yf


def run_backtest(
    ticker="SPY",
    start_date="2018-01-01",
    end_date="2025-01-01",
    short_window=20,
    long_window=50,
    regime_window=200,
    position_size=0.50,
    trading_cost=0.001,
    initial_capital=10000
):
    """
    Run a moving-average crossover backtest with:
    - 200-day market regime filter
    - transaction cost adjustment
    - position sizing
    - performance metrics
    """

    raw_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if raw_data.empty:
        raise ValueError(f"No data downloaded for ticker: {ticker}")

    # Handle yfinance multi-level columns safely
    if isinstance(raw_data.columns, pd.MultiIndex):
        close_series = raw_data["Close"]
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]
    else:
        close_series = raw_data["Close"]

    # Create clean dataframe
    data = pd.DataFrame()
    data["Close"] = close_series.astype(float)
    data.dropna(inplace=True)

    # Daily returns
    data["Daily_Return"] = data["Close"].pct_change()

    # Moving averages
    data["MA_Short"] = data["Close"].rolling(window=short_window).mean()
    data["MA_Long"] = data["Close"].rolling(window=long_window).mean()
    data["MA_Regime"] = data["Close"].rolling(window=regime_window).mean()

    # Market regime filter
    data["Market_Regime"] = np.where(data["Close"] > data["MA_Regime"], 1, 0)

    # Trading signal
    data["Signal"] = np.where(
        (data["MA_Short"] > data["MA_Long"]) & (data["Market_Regime"] == 1),
        1,
        0
    )

    # Avoid look-ahead bias
    data["Position"] = data["Signal"].shift(1)

    # Strategy returns
    data["Strategy_Return"] = data["Position"] * data["Daily_Return"]

    # Transaction cost
    data["Trade_Event"] = data["Position"].diff().abs().fillna(0)

    data["Strategy_Return_After_Cost"] = (
        data["Strategy_Return"] - (data["Trade_Event"] * trading_cost)
    )

    # Position sizing
    data["Strategy_Return_Final"] = data["Strategy_Return_After_Cost"] * position_size

    data.dropna(inplace=True)

    if data.empty:
        raise ValueError(
            "Not enough data after calculations. Try a longer date range or smaller moving-average windows."
        )

    # Growth curves
    data["Buy_Hold_Growth"] = (1 + data["Daily_Return"]).cumprod()
    data["Strategy_Growth"] = (1 + data["Strategy_Return_Final"]).cumprod()

    # Drawdowns
    data["Buy_Hold_Peak"] = data["Buy_Hold_Growth"].cummax()
    data["Strategy_Peak"] = data["Strategy_Growth"].cummax()

    data["Buy_Hold_Drawdown"] = (
        data["Buy_Hold_Growth"] - data["Buy_Hold_Peak"]
    ) / data["Buy_Hold_Peak"]

    data["Strategy_Drawdown"] = (
        data["Strategy_Growth"] - data["Strategy_Peak"]
    ) / data["Strategy_Peak"]

    # Performance metrics
    buy_hold_return = data["Buy_Hold_Growth"].iloc[-1] - 1
    strategy_return = data["Strategy_Growth"].iloc[-1] - 1

    buy_hold_volatility = data["Daily_Return"].std() * np.sqrt(252)
    strategy_volatility = data["Strategy_Return_Final"].std() * np.sqrt(252)

    buy_hold_sharpe = (
        (data["Daily_Return"].mean() * 252) / buy_hold_volatility
        if buy_hold_volatility != 0 else np.nan
    )

    strategy_sharpe = (
        (data["Strategy_Return_Final"].mean() * 252) / strategy_volatility
        if strategy_volatility != 0 else np.nan
    )

    buy_hold_max_drawdown = data["Buy_Hold_Drawdown"].min()
    strategy_max_drawdown = data["Strategy_Drawdown"].min()

    buy_hold_final_value = initial_capital * data["Buy_Hold_Growth"].iloc[-1]
    strategy_final_value = initial_capital * data["Strategy_Growth"].iloc[-1]

    # Trade counts
    data["Trade"] = data["Signal"].diff()
    buy_trades = (data["Trade"] == 1).sum()
    sell_trades = (data["Trade"] == -1).sum()

    # Summary table
    summary = pd.DataFrame({
        "Strategy": ["Buy and Hold", "Quant Strategy"],
        "Ticker": [ticker, ticker],
        "Short Window": [np.nan, short_window],
        "Long Window": [np.nan, long_window],
        "Regime Window": [np.nan, regime_window],
        "Position Size": [1.0, position_size],
        "Trading Cost": [0.0, trading_cost],
        "Total Return (%)": [buy_hold_return * 100, strategy_return * 100],
        "Volatility (%)": [buy_hold_volatility * 100, strategy_volatility * 100],
        "Sharpe Ratio": [buy_hold_sharpe, strategy_sharpe],
        "Max Drawdown (%)": [buy_hold_max_drawdown * 100, strategy_max_drawdown * 100],
        "Final Value (R)": [buy_hold_final_value, strategy_final_value],
        "Buy Trades": [np.nan, buy_trades],
        "Sell Trades": [np.nan, sell_trades]
    })

    return data, summary
