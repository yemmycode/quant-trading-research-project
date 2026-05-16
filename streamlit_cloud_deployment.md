# Streamlit Cloud Deployment Notes

## Deployment Platform

This project can be deployed on Streamlit Community Cloud from GitHub.

## Required Deployment Settings

- Repository: your GitHub quant trading project repository
- Branch: main
- Main file path: app.py

## Required Secrets

In Streamlit Cloud app settings, add:

DASHBOARD_PASSWORD = "your-secure-demo-password"

Do not commit `.env` or `.streamlit/secrets.toml` to GitHub.

## Safety Settings

Before deployment, confirm in `config.py`:

`LIVE_TRADING_ENABLED = False`
`REQUIRE_MANUAL_CONFIRMATION = True`

The deployed demo must remain a research and paper trading simulator only.

## Deployment Steps

1. Push the latest code to GitHub.
2. Log in to Streamlit Community Cloud with GitHub.
3. Create a new app.
4. Select the repository.
5. Select the `main` branch.
6. Set the main file path to `app.py`.
7. Add secrets in TOML format.
8. Deploy.

## Post-Deployment Test

- Confirm login works.
- Confirm Moving Average backtest works.
- Confirm RSI backtest works.
- Confirm paper trading works.
- Confirm manual order ticket remains paper-only.
- Confirm emergency stop works.
- Confirm database viewer does not expose private local data.