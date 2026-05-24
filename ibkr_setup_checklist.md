# IBKR Setup Checklist

## Account and Platform

- [ ] Open or confirm Interactive Brokers account
- [ ] Confirm access to paper trading account
- [ ] Install Trader Workstation or IB Gateway
- [ ] Login to paper trading environment

## TWS / Gateway API Settings

- [ ] Open Global Configuration
- [ ] Go to API settings
- [ ] Enable ActiveX and Socket Clients
- [ ] Confirm socket port
- [ ] Use TWS paper port 7497 for first test
- [ ] Keep Read-Only API enabled for first account/position tests
- [ ] Create API message log file if needed
- [ ] Confirm trusted IP is localhost / 127.0.0.1

## Python Environment

- [x] Install IBKR Python package or ib_insync
- [x] Confirm package imports successfully
- [ ] Confirm project requirements.txt is updated

## Project Secrets

- [x] Add IBKR_HOST to .env locally
- [x] Add IBKR_PORT to .env locally
- [x] Add IBKR_CLIENT_ID to .env locally
- [x] Add IBKR_TRADING_MODE to .env locally
- [ ] Do not commit .env

## First Connection Test

- [ ] Confirm TWS or IB Gateway is running
- [ ] Confirm logged into paper account
- [ ] Connect in read-only mode
- [ ] Print connection status
- [ ] Disconnect safely

## Safety Before Paper Orders

- [ ] EXECUTION_MODE = BROKER_PAPER
- [ ] DEFAULT_BROKER = ibkr
- [ ] ALLOW_LIVE_TRADING = False
- [ ] LIVE_TRADING_ENABLED = False
- [ ] Manual confirmation required
- [ ] Emergency stop working
- [ ] Order logs enabled

## Safety Before Live Trading

- [ ] 30-day broker paper test completed
- [ ] No unresolved execution bugs
- [ ] Risk manager verified
- [ ] Emergency stop verified
- [ ] Manual confirmation verified
- [ ] Very small capital plan prepared

## Lesson 66 Connection Test

- [ ] TWS or IB Gateway opened
- [ ] Logged into paper trading environment
- [ ] API socket clients enabled
- [ ] Read-Only API enabled for first connection test
- [ ] Port confirmed
- [ ] test_ibkr_connection.py created
- [ ] Connection test completed successfully

## Lesson 67 Account Info Test

- [ ] test_ibkr_account_info.py created
- [ ] TWS or IB Gateway open
- [ ] Logged into paper trading
- [ ] API socket enabled
- [ ] Account summary retrieved successfully
- [ ] No orders placed

## Lesson 68 Positions Test

- [ ] test_ibkr_positions.py created
- [ ] TWS or IB Gateway open
- [ ] Logged into paper trading
- [ ] API socket enabled
- [ ] Positions retrieved successfully
- [ ] No orders placed

## Lesson 69 Market Data Test

- [ ] test_ibkr_market_data.py created
- [ ] TWS or IB Gateway open
- [ ] Logged into paper trading
- [ ] API socket enabled
- [ ] Delayed market data requested
- [ ] Contract qualified successfully
- [ ] Market data retrieved successfully
- [ ] No orders placed

## Lesson 70 Contract Builder

- [ ] ibkr_contracts.py created
- [ ] US stock/ETF contract builder created
- [ ] Allowed ticker validation active
- [ ] Contract builder test script created
- [ ] Contract builder test passed
- [ ] No orders placed

## Lesson 71 Order Builder

- [ ] ibkr_orders.py created
- [ ] Market order builder created
- [ ] Limit order builder created
- [ ] Order validation active
- [ ] Order builder test script created
- [ ] Order builder test passed
- [ ] No broker connection attempted
- [ ] No orders placed

## Lesson 72 IBKR Paper Order Submission

- [ ] EXECUTION_MODE set to BROKER_PAPER
- [ ] DEFAULT_BROKER set to ibkr
- [ ] ALLOW_LIVE_TRADING remains False
- [ ] IBKR_TRADING_MODE is paper
- [ ] IBKR_READ_ONLY is false only for paper order test
- [ ] IBKR_ENABLE_ORDERS is true
- [ ] TWS Paper is open
- [ ] API socket enabled
- [ ] Read-Only API unchecked in TWS for paper order test
- [ ] test_ibkr_submit_paper_order.py created
- [ ] Paper limit order submitted successfully
- [ ] Paper test order cancelled manually in TWS
- [ ] No live orders placed

## Lesson 73 IBKR Paper Order Status

- [ ] get_open_orders method added
- [ ] get_all_trades method added
- [ ] get_order_status method added
- [ ] test_ibkr_order_status.py created
- [ ] TWS Paper or IB Gateway open
- [ ] API socket enabled
- [ ] Open orders retrieved successfully
- [ ] Order status checked successfully
- [ ] No orders placed
- [ ] No orders cancelled

## Lesson 74 IBKR Paper Order Cancellation

- [ ] cancel_order method added to IBKRBroker
- [ ] test_ibkr_cancel_order.py created
- [ ] TWS Paper or IB Gateway open
- [ ] API socket enabled
- [ ] Read-Only API unchecked only for paper cancellation test
- [ ] Open paper orders listed successfully
- [ ] Paper order cancellation tested
- [ ] No live orders placed
- [ ] Returned .env to safe mode after testing

## Lesson 75 Broker Risk Manager

- [ ] RiskManager updated with broker-specific approval checks
- [ ] Unsupported tickers blocked
- [ ] Missing manual confirmation blocked
- [ ] Oversized position blocked
- [ ] Short selling blocked
- [ ] Existing-position SELL allowed
- [ ] IBKR paper order script connected to risk manager
- [ ] No live trading enabled

## Lesson 76 Trade Audit Log

- [ ] trade_audit.py created
- [ ] test_trade_audit.py created
- [ ] trade audit logger tested
- [ ] IBKR paper order submission script connected to audit logger
- [ ] view_trade_audit_log.py created
- [ ] logs folder excluded from GitHub
- [ ] No live trading enabled

## Lesson 77 Persistent Emergency Stop

- [ ] safety_manager.py created
- [ ] test_safety_manager.py created
- [ ] Persistent emergency stop JSON state added
- [ ] Risk manager connected to persistent emergency stop
- [ ] Streamlit emergency stop controls added
- [ ] safety folder excluded from GitHub
- [ ] Emergency stop activation tested
- [ ] Emergency stop deactivation tested
- [ ] Broker order blocked while emergency stop is active

## Lesson 78 Broker Manual Approval Ticket

- [ ] Broker Manual Approval Ticket added to Streamlit
- [ ] Emergency stop displayed before order submission
- [ ] Manual confirmation checkbox added
- [ ] Broker risk check button added
- [ ] Submit IBKR Paper Order button added
- [ ] Audit logging connected
- [ ] IBKR paper order tested from dashboard
- [ ] No live trading enabled
- [ ] .env returned to safe mode after testing

## Lesson 79 Live Broker Signal Generator

- [ ] live_signal.py created
- [ ] test_live_signal.py created
- [ ] Latest signal generated successfully
- [ ] Streamlit live signal section added
- [ ] Signal action displayed in dashboard
- [ ] Signal audit event logged
- [ ] No broker order submitted automatically

## Lesson 80 Signal to Order Proposal

- [ ] order_proposal.py created
- [ ] test_order_proposal.py created
- [ ] BUY signal converts to proposed BUY order
- [ ] SELL signal converts to proposed SELL order only if position exists
- [ ] HOLD creates no order
- [ ] STAY IN CASH creates no order
- [ ] Streamlit proposal section added
- [ ] Proposal audit logging added
- [ ] No broker order submitted automatically

## Lesson 81 Signal Review Page

- [ ] Signal Review Page added to Streamlit
- [ ] Latest signal displayed
- [ ] Emergency stop status displayed
- [ ] Latest order proposal displayed
- [ ] Pre-trade recommendation displayed
- [ ] Signal review decision audit logging added
- [ ] No broker order submitted automatically

## Lesson 82 Execute Signal in IBKR Paper Mode

- [ ] Broker ticket can load latest actionable order proposal
- [ ] Proposal ticker loads into broker ticket
- [ ] Proposal side loads into broker ticket
- [ ] Proposal quantity loads into broker ticket
- [ ] Proposal order type loads into broker ticket
- [ ] Proposal limit price loads into broker ticket
- [ ] Risk check works with loaded proposal
- [ ] Manual confirmation still required
- [ ] IBKR paper order submission still requires explicit button click
- [ ] No automatic broker submission added
- [ ] No live trading enabled

## Lesson 83 30-Day IBKR Paper Trading Test Framework

- [ ] paper_test_tracker.py created
- [ ] test_paper_test_tracker.py created
- [ ] Paper test tracker tested
- [ ] paper_test folder excluded from GitHub
- [ ] 30-Day IBKR Paper Trading Test dashboard section added
- [ ] Paper test event logging added
- [ ] Paper test CSV download added
- [ ] Dashboard paper order submission connected to paper test tracker
- [ ] No live trading enabled

## Lesson 84 Daily Paper Trading Report

- [ ] Daily report functions added to paper_test_tracker.py
- [ ] test_daily_paper_report.py created
- [ ] Daily paper report tested
- [ ] Daily Paper Trading Report dashboard section added
- [ ] Daily report metrics displayed
- [ ] Daily report CSV download added
- [ ] No broker connection required
- [ ] No live trading enabled

## Lesson 85 Weekly Paper Trading Review

- [ ] Weekly review functions added to paper_test_tracker.py
- [ ] test_weekly_paper_review.py created
- [ ] Weekly review tested
- [ ] Weekly Paper Trading Review dashboard section added
- [ ] Weekly metrics displayed
- [ ] Weekly recommendation displayed
- [ ] Weekly review CSV download added
- [ ] No broker connection required
- [ ] No live trading enabled

## Lesson 86 Live Trading Readiness Checklist

- [ ] live_readiness.py created
- [ ] test_live_readiness.py created
- [ ] Live readiness checklist tested
- [ ] readiness folder excluded from GitHub
- [ ] Live Trading Readiness Checklist added to Streamlit
- [ ] Readiness score displayed
- [ ] Missing readiness items displayed
- [ ] Checklist editing and saving added
- [ ] No live trading enabled

## Lesson 87 Live Mode Lock

- [ ] live_mode_lock.py created
- [ ] test_live_mode_lock.py created
- [ ] Live mode lock tested
- [ ] Live mode remains locked by default
- [ ] Streamlit Live Mode Lock section added
- [ ] Failed checks displayed
- [ ] No live trading enabled

## Lesson 88 Live Trading Warning Screen

- [ ] live_warning.py created
- [ ] test_live_warning.py created
- [ ] Live warning acknowledgement tested
- [ ] Live mode lock updated to require warning acknowledgement
- [ ] Live Trading Warning Screen added to Streamlit
- [ ] Warning acknowledgement audit logging added
- [ ] No live trading enabled

## Lesson 89 Live Order Dry Run Mode

- [ ] live_order_dry_run.py created
- [ ] test_live_order_dry_run.py created
- [ ] Dry run tested
- [ ] Live Order Dry Run Mode added to Streamlit
- [ ] Dry run confirms no broker submission
- [ ] Dry run checks emergency stop
- [ ] Dry run checks live warning acknowledgement
- [ ] Dry run checks live mode lock
- [ ] Dry run checks risk manager
- [ ] No live trading enabled

## Lesson 90 IBKR Live Read-Only Connection

- [ ] test_ibkr_live_read_only.py created
- [ ] .env prepared with IBKR_TRADING_MODE=live
- [ ] .env prepared with IBKR_PORT=7496
- [ ] .env kept with IBKR_READ_ONLY=true
- [ ] .env kept with IBKR_ENABLE_ORDERS=false
- [ ] TWS Live API read-only settings reviewed
- [ ] Live read-only connection tested successfully
- [ ] No live orders placed
- [ ] No live trading enabled

## Lesson 91 Broker Environment Safety Panel

- [ ] broker_environment.py created
- [ ] test_broker_environment.py created
- [ ] Broker environment classifier tested
- [ ] Broker Environment Safety Panel added to Streamlit
- [ ] Environment status displayed
- [ ] Warnings and blockers displayed
- [ ] No broker settings changed automatically
- [ ] No live trading enabled

## Lesson 92 Environment Reset Checklist

- [ ] environment_reset.py created
- [ ] test_environment_reset.py created
- [ ] Environment reset checklist tested
- [ ] Environment Reset Checklist added to Streamlit
- [ ] Reset score displayed
- [ ] Missing reset items displayed
- [ ] Reset checklist audit logging added
- [ ] No environment settings changed automatically
- [ ] No live trading enabled

## Lesson 93 System Health Check Dashboard

- [ ] system_health.py created
- [ ] test_system_health.py created
- [ ] System health test executed
- [ ] Streamlit System Health Check Dashboard added
- [ ] Required files checked
- [ ] Module imports checked
- [ ] Config safety checked
- [ ] Safety systems checked
- [ ] Local logs checked
- [ ] No broker connection required
- [ ] No live trading enabled

## Lesson 94 Deployment Health Check

- [ ] deployment_health.py created
- [ ] test_deployment_health.py created
- [ ] Local deployment health test executed
- [ ] Deployment Health Check added to Streamlit
- [ ] Runtime environment detected
- [ ] Feature availability matrix displayed
- [ ] IBKR localhost availability explained
- [ ] Streamlit Cloud limitations clearly shown
- [ ] No broker order submitted
- [ ] No live trading enabled

## Lesson 95 Secure Broker Architecture Plan

- [ ] secure_broker_architecture.md created
- [ ] secure_broker_architecture.py created
- [ ] test_secure_broker_architecture.py created
- [ ] Secure broker architecture test executed
- [ ] Secure Broker Architecture Plan added to Streamlit
- [ ] Streamlit Cloud broker limitation documented
- [ ] Local paper trading architecture documented
- [ ] Future VPS / IB Gateway architecture documented
- [ ] No broker connection required
- [ ] No live trading enabled

## Lesson 96 SQLite Trading Database Foundation

- [ ] trading_database.py created
- [ ] test_trading_database.py created
- [ ] SQLite database initialized
- [ ] signals table created
- [ ] order_proposals table created
- [ ] risk_checks table created
- [ ] broker_orders table created
- [ ] audit_events table created
- [ ] system_events table created
- [ ] database folder excluded from GitHub
- [ ] SQLite Trading Database section added to Streamlit
- [ ] system_health.py updated
- [ ] No broker connection required
- [ ] No live trading enabled

## Lesson 97 Unified Order State Manager

- [ ] order_state_manager.py created
- [ ] test_order_state_manager.py created
- [ ] Order state tables initialized
- [ ] Order lifecycle state test executed
- [ ] Unified Order State Manager added to Streamlit
- [ ] order_state_events table added
- [ ] order_current_state table added
- [ ] SQLite dashboard updated to view order state tables
- [ ] system_health.py updated
- [ ] No broker connection required
- [ ] No live trading enabled

## Lesson 98 Duplicate Order Protection

- [ ] duplicate_order_guard.py created
- [ ] test_duplicate_order_guard.py created
- [ ] Duplicate guard test executed
- [ ] Duplicate Order Guard added to Streamlit
- [ ] Active duplicate order detection added
- [ ] Broker Manual Approval Ticket patched with duplicate guard
- [ ] Successful paper submission connected to order state tracking
- [ ] system_health.py updated
- [ ] No broker connection required for duplicate checks
- [ ] No live trading enabled

## Lesson 99 Position-Aware Signal Execution

- [ ] position_aware_execution.py created
- [ ] test_position_aware_execution.py created
- [ ] Position-aware logic tested
- [ ] Position-Aware Signal Execution added to Streamlit
- [ ] BUY while already long blocked by default
- [ ] SELL while flat blocked by default
- [ ] Broker Manual Approval Ticket patched with position-aware gate
- [ ] system_health.py updated
- [ ] No broker connection required for position check
- [ ] No live trading enabled

## Lesson 100 Broker Account Snapshot Module

- [ ] broker_account_snapshot.py created
- [ ] test_broker_account_snapshot.py created
- [ ] Broker account snapshot test executed
- [ ] Broker Account Snapshot added to Streamlit
- [ ] Snapshot summary displayed
- [ ] Position snapshot displayed
- [ ] system_health.py updated
- [ ] No broker order submitted
- [ ] No live trading enabled

## Lesson 101 Connect Account Snapshot to Position-Aware Execution

- [ ] Snapshot-aware position functions added
- [ ] test_snapshot_position_aware_execution.py created
- [ ] Snapshot position-aware test executed
- [ ] Position-Aware dashboard updated to prefer Broker Account Snapshot
- [ ] Manual broker ticket position gate updated to prefer snapshot
- [ ] Syntax checks passed
- [ ] No broker order submitted
- [ ] No live trading enabled

## Lesson 102 Market Hours Awareness

- [ ] pandas-market-calendars added to requirements.txt
- [ ] market_hours.py created
- [ ] test_market_hours.py created
- [ ] Market hours test executed
- [ ] Market Hours Awareness added to Streamlit
- [ ] Manual broker ticket patched with market-hours gate
- [ ] system_health.py updated
- [ ] Syntax checks passed
- [ ] No broker order submitted
- [ ] No live trading enabled