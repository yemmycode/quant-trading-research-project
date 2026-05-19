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