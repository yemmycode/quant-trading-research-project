# Cleanup Recommendations

## Main Problem

The project has many useful modules, but they are not yet organized around one central workflow.

The goal now is not to delete everything, but to separate:

```text
Core trading workflow
Support/admin tools
Testing tools
Backup files
Documentation
```

---

## Keep as Core Workflow

```text
app.py
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

## Keep as Support/Admin

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

## Keep as Tests

All files beginning with:

```text
test_
```

should remain, but they should be organized logically.

---

## Move or Ignore Backup Files

Files containing:

```text
backup
```

should not remain in the main working area long term.

Recommended future action:

```text
Create backups/ folder
Move backup files there
Add backups/ to .gitignore
```

Do not delete backups until the project is stable.

---

## Dashboard Cleanup Recommendation

The dashboard should be rearranged into:

```text
1. Trading Control Center
2. Portfolio & Orders
3. Safety & Readiness
4. System Admin
5. Documentation
```

The next development step should be to build the Trading Control Center.