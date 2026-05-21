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