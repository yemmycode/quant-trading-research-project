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

- [ ] Add IBKR_HOST to .env locally
- [ ] Add IBKR_PORT to .env locally
- [ ] Add IBKR_CLIENT_ID to .env locally
- [ ] Add IBKR_TRADING_MODE to .env locally
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