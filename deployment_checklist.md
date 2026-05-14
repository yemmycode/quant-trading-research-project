# Demo Deployment Preparation Checklist

## Purpose

This checklist prepares the Quant Trading Research Dashboard for safe demo deployment.

The project is currently designed for:

- Quant strategy research
- Backtesting
- Paper trading simulation
- Dashboard-based analysis
- Educational demonstration

It must not be presented as a guaranteed profit system, investment advisory tool, or live trading service.

---

## 1. Secrets and Passwords

Before deployment:

- Ensure `.env` is not committed to GitHub.
- Ensure `.env` is listed inside `.gitignore`.
- Ensure `DASHBOARD_PASSWORD` is not hardcoded with a private password inside `config.py`.
- Use environment variables on the deployment platform.
- Keep `.env.example` in the repository as a template only.

Correct setup:

`DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "demo-password")`

Do not expose real passwords in:

- GitHub
- README
- Screenshots
- Public videos
- Shared zip files

---

## 2. GitHub Readiness

Before pushing or deploying:

- Confirm `README.md` is updated.
- Confirm `requirements.txt` includes all packages.
- Confirm `.gitignore` excludes generated files and secrets.
- Confirm the project runs locally after a fresh restart.
- Confirm no private API keys are committed.

Useful commands:

`git status`
`git add .`
`git commit -m "Prepare project for demo deployment"`
`git push`

---

## 3. Required Python Packages

The `requirements.txt` file should include:

- pandas
- numpy
- matplotlib
- yfinance
- openpyxl
- streamlit
- python-dotenv

If more packages are added later, update `requirements.txt`.

---

## 4. Streamlit Dashboard Readiness

Before demo use:

- Confirm the login screen works.
- Confirm logout works.
- Confirm dashboard password is loaded from an environment variable.
- Confirm the Moving Average strategy runs.
- Confirm the RSI strategy runs.
- Confirm charts display correctly.
- Confirm paper trading mode works.
- Confirm database viewer does not crash.
- Confirm manual order ticket uses Paper Broker only.
- Confirm Emergency Stop blocks paper orders.

---

## 5. Trading Safety

The demo must keep live trading disabled.

Config settings should remain:

`LIVE_TRADING_ENABLED = False`
`REQUIRE_MANUAL_CONFIRMATION = True`
`EMERGENCY_STOP = False`

For demo safety, the dashboard should clearly state:

- No live trades are placed.
- All orders are simulated.
- Results are educational only.
- Backtests do not guarantee future performance.

---

## 6. Broker API Safety

Before any broker integration:

- Use paper/sandbox account only.
- Never store broker keys in code.
- Use environment variables for API keys.
- Add manual confirmation before order submission.
- Add maximum daily loss control.
- Add maximum drawdown stop.
- Add allowed tickers list.
- Add emergency stop.
- Add order logging.

Live trading must not be enabled until the platform has passed extended paper testing.

---

## 7. Data and Database Safety

The local SQLite database should not be pushed to GitHub.

Make sure `.gitignore` includes:

- `data/*.db`
- `data/*.sqlite`

For public demos:

- Use sample/demo data only.
- Avoid exposing personal trading records.
- Avoid exposing account details.
- Avoid exposing private order logs.

---

## 8. Public Demo Positioning

When showing the platform publicly, describe it as:

- Quant research dashboard
- Backtesting and paper trading simulator
- Educational trading analytics tool
- Portfolio project

Do not describe it as:

- Guaranteed profit bot
- Investment advisor
- Signal-selling service
- Copy-trading platform
- Managed trading service

---

## 9. Compliance Caution

If the platform is offered to other people for trading signals, recommendations, copy-trading, portfolio management, or investment advice, regulatory approval may be required.

Before public commercial use:

- Consult a qualified financial services compliance professional.
- Review FSCA requirements in South Africa.
- Avoid giving personalized investment advice unless properly licensed.
- Avoid managing other people's money without authorization.

---

## 10. Final Pre-Deployment Checklist

Before deployment, confirm:

- [ ] App runs locally with `streamlit run app.py`
- [ ] Password login works
- [ ] Password is loaded from environment variable
- [ ] `.env` is ignored by Git
- [ ] `requirements.txt` is updated
- [ ] Dashboard warning/disclaimer is visible
- [ ] Live trading is disabled
- [ ] Paper Broker is used only
- [ ] Emergency Stop works
- [ ] README is updated
- [ ] No private keys or passwords are in GitHub
- [ ] GitHub repo is clean and professional

---

## Recommended Demo Message

This dashboard is a quant trading research and paper trading simulator.

It is designed for educational analysis, backtesting, and strategy comparison.

It does not place live trades and does not provide financial advice.

Backtested and simulated results do not guarantee future performance.