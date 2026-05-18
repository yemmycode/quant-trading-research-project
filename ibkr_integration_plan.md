# IBKR Integration Plan and Requirements

## Purpose

This document prepares the Quant Trading Research Project for Interactive Brokers integration.

The first target market is the United States.

The first target instruments are:

- US stocks
- US ETFs
- Highly liquid large-cap instruments

Initial examples:

- SPY
- QQQ
- AAPL
- MSFT

The system must connect to IBKR Paper Trading first before any live trading is considered.

---

## Current Project Position

The project currently supports:

- backtesting
- multi-strategy research
- parameter optimization
- Streamlit dashboard
- paper broker simulation
- risk manager
- order manager
- manual confirmation
- emergency stop
- broker factory

The project does not yet connect to any real broker.

---

## IBKR Connection Options

Interactive Brokers offers several API routes. For this project, the preferred route is:

TWS API / IB Gateway API

This requires either:

- Trader Workstation running locally, or
- IB Gateway running locally or on a controlled server

The API communicates through a socket connection.

---

## TWS / IB Gateway Requirements

Before Python can connect to IBKR, the user must:

1. Open an Interactive Brokers account.
2. Enable paper trading account access.
3. Install Trader Workstation or IB Gateway.
4. Log into the paper trading environment first.
5. Enable API socket connections.
6. Confirm the correct API socket port.
7. Keep Read-Only API enabled initially for account/position testing.
8. Disable Read-Only API only when ready to test paper orders.

---

## Default IBKR API Ports

Common default ports:

- TWS Live: 7496
- TWS Paper: 7497
- IB Gateway Live: 4001
- IB Gateway Paper: 4002

The port configured inside TWS or IB Gateway must match the port used by the Python client.

---

## Recommended First Connection Settings

For first testing:

- Host: 127.0.0.1
- Port: 7497
- Client ID: 1
- Mode: Paper
- Read-only first: True

Only after read-only connection works should paper order testing be enabled.

---

## Required Environment Variables

The project should use environment variables or Streamlit secrets for IBKR settings.

Planned variables:

- IBKR_HOST=127.0.0.1
- IBKR_PORT=7497
- IBKR_CLIENT_ID=1
- IBKR_ACCOUNT_ID=
- IBKR_TRADING_MODE=paper
- IBKR_READ_ONLY=true

Do not store sensitive broker details directly in GitHub.

---

## Python Package Direction

There are two practical Python options:

1. Native IBKR TWS API
2. ib_insync wrapper

The native API is official but more verbose.

The ib_insync package is easier for Python workflows and commonly used for research-style projects.

For this project, the recommended first implementation is ib_insync, while keeping the architecture broker-agnostic.

---

## Safety Rules Before IBKR Paper Orders

Before submitting even paper orders through IBKR, the following must be active:

- EXECUTION_MODE must be BROKER_PAPER
- DEFAULT_BROKER must be ibkr
- LIVE_TRADING_ENABLED must remain False
- ALLOW_LIVE_TRADING must remain False
- Manual confirmation must be required
- Emergency stop must be available
- Allowed ticker list must be enforced
- Position size limits must be enforced
- Order log must be active

---

## Safety Rules Before Live Trading

Before live trading can be considered:

- IBKR paper connection must work consistently.
- Account info must load correctly.
- Positions must load correctly.
- Market data must load correctly.
- Paper orders must submit correctly.
- Paper order status must update correctly.
- Cancel order workflow must work.
- Emergency stop must block orders.
- Manual confirmation must be required.
- No unresolved bugs should remain.
- Very small capital only should be used for first live testing.

---

## Initial Allowed Instruments

Start with simple US stocks and ETFs only:

- SPY
- QQQ
- AAPL
- MSFT

Avoid initially:

- options
- futures
- forex
- crypto
- margin
- short selling
- leveraged ETFs
- illiquid penny stocks

---

## Live Trading Policy

The system must not start with automatic live trading.

The first live phase should be manual-confirmation only:

Signal generated -> Risk check -> User reviews -> User confirms -> Broker order submitted

Fully automated live trading should only be considered after extensive paper testing and live testing review.

---

## Next Implementation Lessons

- Lesson 64: Install and test IBKR Python package
- Lesson 65: Add IBKR config and secrets
- Lesson 66: Connect to IBKR paper account
- Lesson 67: Read IBKR paper account info
- Lesson 68: Read IBKR paper positions
- Lesson 69: Read IBKR market data
- Lesson 70: Build IBKR contract builder
- Lesson 71: Build IBKR paper order builder
- Lesson 72: Submit IBKR paper orders only
- Lesson 73: Monitor IBKR paper order status
- Lesson 74: Cancel IBKR paper orders

---

## Risk Disclaimer

This integration is for educational and research purposes first.

Trading involves risk and can result in capital loss.

Backtested and paper-traded performance does not guarantee future live performance.

Live trading must remain disabled until the platform has passed broker paper testing and manual live-readiness checks.