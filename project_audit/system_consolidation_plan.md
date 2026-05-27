# Quant Trading System Consolidation Plan

## Current Stage

The system is now in consolidation mode.

The objective is no longer to add random modules. The objective is to connect existing modules into one clean end-to-end paper trading workflow.

---

## Final Core Trading Workflow

The daily paper trading workflow should be:

```text
1. Select ticker
2. Download market data
3. Generate latest strategy signal
4. Create order proposal
5. Capture broker account snapshot
6. Check market hours
7. Run position-aware check
8. Run duplicate-order guard
9. Run price validation
10. Run risk manager
11. Require manual confirmation
12. Submit IBKR paper order
13. Save order state
14. Track broker/order status
15. Record fill and slippage
16. Update audit log
17. Review daily report
```

---

## Core Workflow Modules

These modules should power the actual trading workflow:

```text
config.py
live_signal.py
order_proposal.py
broker_account_snapshot.py
market_hours.py
position_aware_execution.py
duplicate_order_guard.py
price_validation.py
risk_manager.py
safety_manager.py
broker_environment.py
order_state_manager.py
fill_slippage_tracker.py
trade_audit.py
trading_database.py
brokers/
strategies/
```

---

## Support/Admin Modules

These modules should support monitoring, safety, testing, and operations:

```text
system_health.py
deployment_health.py
secure_broker_architecture.py
live_readiness.py
live_mode_lock.py
live_warning.py
live_order_dry_run.py
environment_reset.py
error_notifier.py
test_runner.py
```

---

## Dashboard Restructure Plan

The Streamlit dashboard should be reorganized into five main sections:

### 1. Trading Control Center

This should become the main working screen.

It should include:

```text
Ticker selector
Strategy selector
Generate signal
Order proposal
Account snapshot
Market hours result
Position-aware result
Duplicate-order result
Price validation result
Risk manager result
Manual confirmation
Submit IBKR paper order
Order state result
Audit result
```

### 2. Portfolio & Orders

This should include:

```text
Portfolio overview
Broker account snapshot
Open positions
Order state manager
Fill and slippage tracking
```

### 3. Safety & Readiness

This should include:

```text
Emergency stop
Broker environment safety panel
Live readiness checklist
Live mode lock
Live warning screen
Environment reset checklist
```

### 4. System Admin

This should include:

```text
System health check
Deployment health check
Error notification system
Automated test runner
SQLite database viewer
```

### 5. Documentation

This should include:

```text
Secure broker architecture plan
IBKR setup checklist
30-day paper testing plan
```

---

## Immediate Next Steps

### C1: System Consolidation Audit

Status: In progress.

### C2: Create Trading Control Center

Build one clean dashboard section that connects the full workflow.

### C3: Connect Database Logging

Ensure signal, proposal, risk check, order state, broker response, fills, and errors are saved consistently.

### C4: Clean Existing Dashboard

Move support panels below the main Trading Control Center.

### C5: Run End-to-End Paper Trade Test

Run one controlled paper trade workflow from signal to order state.

### C6: Begin 30-Day Paper Trading Validation

Only after the workflow is stable.

---

## Rule Going Forward

No new feature should be added unless it directly supports the final core workflow or fixes a blocking issue.