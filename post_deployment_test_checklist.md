# Post-Deployment Test Checklist

## Purpose

This checklist is used after deploying the Quant Trading Research Dashboard to Streamlit Cloud.

---

## 1. Login Test

- [ ] App opens successfully
- [ ] Login page appears
- [ ] Wrong password is rejected
- [ ] Correct password is accepted
- [ ] Logout button works

---

## 2. Backtest Test

Test Moving Average Strategy:

- [ ] Select Moving Average
- [ ] Ticker: SPY
- [ ] Start Date: 2018-01-01
- [ ] End Date: 2025-01-01
- [ ] Short MA: 20
- [ ] Long MA: 50
- [ ] Run Backtest
- [ ] Summary table appears
- [ ] Equity curve appears
- [ ] Drawdown chart appears
- [ ] Trade log appears or no-trade message appears

Test RSI Strategy:

- [ ] Select RSI
- [ ] Ticker: QQQ
- [ ] RSI Window: 14
- [ ] Oversold: 30
- [ ] Overbought: 70
- [ ] Run Backtest
- [ ] Summary table appears
- [ ] RSI chart appears
- [ ] Trade log appears or no-trade message appears

---

## 3. Paper Trading Test

- [ ] Run paper trading check for moving_average + SPY
- [ ] Latest status appears
- [ ] Recommendation appears
- [ ] Paper equity curve appears
- [ ] Paper trading history updates

---

## 4. Manual Order Ticket Test

- [ ] Paper broker account appears
- [ ] Order preview appears
- [ ] SPY buy order with 5% position size is accepted after confirmation
- [ ] TSLA order is blocked if TSLA is not allowed
- [ ] Position size above max limit is blocked
- [ ] Order log updates

---

## 5. Emergency Stop Test

- [ ] Turn Emergency Stop ON
- [ ] Try simulated order
- [ ] Order is blocked
- [ ] Turn Emergency Stop OFF
- [ ] Order flow works again subject to risk rules

---

## 6. Database Viewer Test

- [ ] paper_trading_history table opens
- [ ] order_log table opens
- [ ] strategy_results table opens
- [ ] Empty tables do not crash app

---

## 7. Cloud Safety Test

- [ ] No real broker API is connected
- [ ] LIVE_TRADING_ENABLED remains False
- [ ] Dashboard disclaimer is visible
- [ ] Secrets are not visible in GitHub
- [ ] .env is not committed
- [ ] .streamlit/secrets.toml is not committed

---

## Notes

Streamlit Cloud file storage may reset when the app restarts. Local CSV and SQLite database records should be treated as temporary in cloud deployment unless connected to persistent external storage.