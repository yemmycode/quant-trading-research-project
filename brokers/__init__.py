
# Broker adapters package
# Keep this file lightweight.
# Do not import IBKR or Alpaca here because Streamlit may load this package at startup.

from broker_factory import get_broker, list_available_brokers
