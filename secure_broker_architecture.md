# Secure Broker Architecture Plan

## Purpose

This document defines the safe architecture path for the quant trading project as it moves from local paper testing toward a more professional broker-connected trading system.

This document does not enable live trading.
This document does not authorize automated trading.
This document is for planning, safety, and system design.

---

## Current Architecture

The current working setup is:

```text
Local Laptop
↓
Streamlit Local App
↓
Interactive Brokers Trader Workstation / IB Gateway
↓
IBKR Paper Account
```

This is suitable for:

- Local paper trading
- Broker connection testing
- Paper order submission
- Paper order cancellation
- Strategy validation
- Manual approval testing
- Audit logging
- Risk manager testing

It is not suitable for unattended live trading.

---

## Streamlit Cloud Limitation

Streamlit Cloud cannot connect directly to a local TWS or IB Gateway running on a personal laptop.

If the app is running on Streamlit Cloud and tries to connect to:

```text
127.0.0.1:7497
```

it is trying to connect to Streamlit Cloud itself, not the laptop.

Therefore:

- IBKR execution must remain local for now.
- Streamlit Cloud can be used for dashboards and reporting.
- Streamlit Cloud should not be treated as the broker execution environment.

---

## Safe Environments

### 1. Local Research Environment

Used for backtesting, strategy experiments, data analysis, signal generation, paper testing, and local dashboard testing.

Recommended mode:

```text
DEFAULT_BROKER=paper or ibkr
EXECUTION_MODE=BACKTEST or BROKER_PAPER
ALLOW_LIVE_TRADING=False
LIVE_TRADING_ENABLED=False
```

### 2. Local IBKR Paper Execution Environment

Used for IBKR paper order testing, account monitoring, open order reading, paper order cancellation, and risk manager validation.

Recommended mode for paper order testing:

```text
IBKR_TRADING_MODE=paper
IBKR_PORT=7497
IBKR_READ_ONLY=false
IBKR_ENABLE_ORDERS=true
ALLOW_LIVE_TRADING=False
LIVE_TRADING_ENABLED=False
```

After testing, return to:

```text
IBKR_READ_ONLY=true
IBKR_ENABLE_ORDERS=false
```

### 3. Streamlit Cloud Review Environment

Used for dashboard viewing, reports, signal review, health checks, documentation, and paper validation summaries.

Not used for IBKR order submission, order cancellation, local TWS connection, or live execution.

Recommended mode:

```text
ALLOW_LIVE_TRADING=False
LIVE_TRADING_ENABLED=False
IBKR_ENABLE_ORDERS=false
```

### 4. Future VPS / Server IB Gateway Environment

This is the future professional broker architecture.

Possible setup:

```text
Secure VPS / Cloud Server
↓
IB Gateway running on server
↓
Trading engine
↓
Risk manager
↓
Audit database
↓
Dashboard / Monitoring interface
```

This requires secure server hardening, secrets management, firewall rules, process monitoring, restart policies, error alerts, database backups, access control, compliance review, and recovery planning.

---

## Security Requirements Before VPS Broker Deployment

Before any VPS or hosted broker execution environment is used, the following must exist:

1. Secure secrets storage
2. No API credentials committed to GitHub
3. Server firewall configured
4. Restricted IP access
5. IB Gateway restart monitoring
6. Persistent database
7. Trade audit logs
8. Error alerts
9. Emergency stop mechanism
10. Duplicate order protection
11. Position-aware execution
12. Manual approval flow
13. Read-only mode
14. Dry-run mode
15. Live mode lock
16. Live warning acknowledgement
17. Backup and recovery plan

---

## Execution Policy

The system must follow this order:

```text
Signal generated
↓
Order proposal created
↓
Signal reviewed
↓
Risk manager approval
↓
Manual confirmation
↓
Broker environment check
↓
Emergency stop check
↓
Duplicate order check
↓
Position check
↓
Dry run
↓
Paper execution
```

Live execution must not be enabled until all paper validation and readiness requirements are complete.

---

## Prohibited Until Future Approval

- Automated live trading
- Trading other people's money
- Margin trading
- Short selling
- Options trading
- Futures trading
- Crypto trading
- High-frequency trading
- Unattended live execution
- Live order submission from Streamlit Cloud
- Public investment advice
- Copy trading for others

---

## Current Recommended Path

```text
Continue local IBKR paper testing
Complete 30-day paper trading validation
Build SQLite trading database
Add duplicate order protection
Add position-aware execution
Add broker account snapshot module
Complete live read-only test
Review readiness checklist
Define small-capital manual live test plan
```

---

## Final Position

The current architecture is suitable for controlled local paper trading only.

It is not yet suitable for live trading.

Live trading should remain locked.