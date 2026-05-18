
# Quant Trading Research Project

## Overview

This project is a Python-based quant trading research system designed to test moving-average trend-following strategies across multiple financial assets.

The system downloads market data, runs backtests, compares strategy performance, generates charts, saves results, and stores each research run in a timestamped folder for reproducibility.

This project is for educational and research purposes only. It is not financial advice and does not guarantee future trading performance.

---

## Strategy Logic

The core strategy is a moving-average crossover system with a long-term market regime filter.

The strategy uses:

- Short moving average
- Long moving average
- 200-day market regime filter
- Transaction cost assumption
- Position sizing

### Buy / Hold Condition

The strategy enters or holds a position when:

- Short moving average is greater than long moving average
- Closing price is above the 200-day moving average

### Exit / Stay Out Condition

The strategy stays out of the market when:

- Short moving average is below or equal to long moving average
- Closing price is below or equal to the 200-day moving average

---

## Project Structure

quant_trading_project/
- README.md
- config.py
- run_batch_tests.py
- generate_charts.py
- run_research_pipeline.py
- strategies/
  - moving_average_strategy.py
- results/
- charts/
- reports/
- logs/
- runs/
- data/
- notebooks/

---

## Main Files

### config.py

Stores project settings such as tickers, dates, moving-average parameter sets, position size, trading cost, and initial capital.

### strategies/moving_average_strategy.py

Contains the reusable run_backtest() function.

### run_batch_tests.py

Runs multiple strategy tests across different tickers and parameter combinations.

### generate_charts.py

Generates equity curve and drawdown charts for the top-performing strategies.

### run_research_pipeline.py

Runs the full research process in one command.

---

## How to Run the Project

Open Git Bash or terminal and navigate to the project folder:

cd "/c/Users/yemi/OneDrive/Desktop/quant_trading_project"

Then run:

python run_research_pipeline.py

---

## Outputs

Each pipeline run creates a timestamped folder inside the runs folder.

Example:

runs/
- 2026-05-12_153000/
  - config_snapshot.py
  - results/
  - charts/
  - logs/

---

## Performance Metrics

The system calculates:

- Total Return
- Volatility
- Sharpe Ratio
- Maximum Drawdown
- Final Portfolio Value
- Number of Buy Trades
- Number of Sell Trades

---

## Current Asset Universe

The default assets are:

- SPY
- QQQ
- AAPL
- MSFT
- TSLA

These can be changed inside config.py.

---

## Current Parameter Sets

The default moving-average combinations are:

- 10 / 50
- 20 / 50
- 20 / 100
- 50 / 200

These can also be changed inside config.py.

---

## Risk Disclaimer

This project is for educational research only.

Backtested results do not guarantee future performance. Real-world trading involves risk, including loss of capital. Trading costs, slippage, liquidity, taxes, execution delays, and emotional decision-making can affect live results.

Do not use this project for live trading without further testing, validation, paper trading, and proper risk management.

---

## IBKR Integration Plan

This project is being prepared for US-market broker integration using Interactive Brokers.

The integration roadmap is documented in:

`ibkr_integration_plan.md`

The first broker-connected phase will use IBKR Paper Trading only.

Live trading must remain disabled until paper testing, broker validation, risk controls, and manual confirmation workflows are fully verified.