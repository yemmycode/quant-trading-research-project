# Broker Connection Plan

## Purpose

This document outlines the future broker API connection plan for the Quant Trading Research Project.

The project is currently designed for:

- backtesting
- strategy research
- chart generation
- paper trading simulation
- dashboard-based research

This project should not place live trades until additional safety controls, broker testing, and paper trading validation have been completed.

---

## Current Project Stage

Current stage:

Research Engine → Streamlit Dashboard → Paper Trading Simulation

Future stage:

Broker Sandbox → Manual Order Confirmation → Small Live Testing

---

## Broker Candidates

### 1. Interactive Brokers

Interactive Brokers is a strong long-term candidate because it offers global market access and mature API options.

Potential use:

- US stocks
- ETFs
- global assets
- paper trading
- long-term professional platform integration

### 2. Alpaca

Alpaca is useful for developer-friendly API learning and paper trading.

Potential use:

- learning broker API structure
- paper trading
- simple API execution testing

### 3. Saxo Bank

Saxo may be useful for professional multi-asset trading access, depending on account access and API eligibility.

Potential use:

- multi-asset trading
- professional API research
- future institutional-style integration

### 4. South African Retail Brokers

Some South African brokers may not provide official public trading APIs for retail algorithmic trading.

Unofficial APIs should not be used for serious trading automation unless the broker officially supports them.

---

## Proposed Broker Architecture

Strategy Signal
      ↓
Risk Manager
      ↓
Order Manager
      ↓
Broker Adapter
      ↓
Broker API

### Strategy Signal

Generates:

- buy signal
- sell signal
- hold signal
- cash signal

### Risk Manager

Checks:

- maximum position size
- maximum daily loss
- maximum drawdown
- allowed tickers
- account exposure
- whether live trading is enabled

### Order Manager

Converts approved signals into order instructions.

### Broker Adapter

Connects to the selected broker API.

Examples:

- Alpaca adapter
- IBKR adapter
- Saxo adapter

---

## Safety Rules

Live trading must remain disabled by default.

Recommended future config settings:

LIVE_TRADING_ENABLED = False
REQUIRE_MANUAL_CONFIRMATION = True
MAX_POSITION_SIZE = 0.10
MAX_DAILY_LOSS = 0.02
MAX_WEEKLY_LOSS = 0.05
MAX_TOTAL_DRAWDOWN = 0.10
ALLOWED_TICKERS = ["SPY", "QQQ"]

---

## Development Roadmap

### Phase 1: Research

- Continue backtesting
- Improve risk metrics
- Improve strategy comparison
- Add more strategies

### Phase 2: Paper Trading

- Strengthen paper trading mode
- Track daily signal history
- Track simulated positions
- Save paper trading logs

### Phase 3: Broker Sandbox

- Study broker API documentation
- Create broker adapter interface
- Connect to paper/sandbox account only
- Test order simulation

### Phase 4: Manual Confirmation Mode

- Generate order recommendation
- Require manual approval before order submission
- Save all order attempts to logs

### Phase 5: Limited Live Testing

Only after long paper testing:

- use very small capital
- no leverage
- strict max loss rules
- manual confirmation
- emergency stop

---

## Risk Disclaimer

This project is for research and educational use.

Backtested and paper-traded results do not guarantee future performance.

Live trading involves risk, including loss of capital.

No live broker connection should be enabled until the system has robust safety controls and has been tested extensively in paper mode.