
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
BROKERS_PATH = CURRENT_FILE.parent
PROJECT_PATH = BROKERS_PATH.parent

if str(BROKERS_PATH) not in sys.path:
    sys.path.append(str(BROKERS_PATH))

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))


from config import (
    DEFAULT_BROKER,
    SUPPORTED_BROKERS,
    EXECUTION_MODE,
    ALLOW_LIVE_TRADING,
    validate_execution_settings
)


def get_broker(
    broker_name=None,
    initial_cash=10000,
    use_database=True,
    paper_mode=True
):
    """
    Return the selected broker adapter.

    This function uses lazy imports so Streamlit does not load IBKR packages
    unless the IBKR broker is actually requested.
    """

    validate_execution_settings()

    if broker_name is None:
        broker_name = DEFAULT_BROKER

    broker_name = broker_name.lower().strip()

    if broker_name not in SUPPORTED_BROKERS:
        raise ValueError(
            f"Unsupported broker: {broker_name}. "
            f"Supported brokers: {SUPPORTED_BROKERS}"
        )

    if broker_name == "paper":
        from paper_broker import PaperBroker

        return PaperBroker(
            initial_cash=initial_cash,
            use_database=use_database
        )

    if broker_name == "ibkr":
        if EXECUTION_MODE == "LIVE_MANUAL" and not ALLOW_LIVE_TRADING:
            raise PermissionError(
                "IBKR live mode is blocked because ALLOW_LIVE_TRADING is False."
            )

        from ibkr_broker import IBKRBroker

        return IBKRBroker(paper_mode=paper_mode)

    if broker_name == "alpaca":
        if EXECUTION_MODE == "LIVE_MANUAL" and not ALLOW_LIVE_TRADING:
            raise PermissionError(
                "Alpaca live mode is blocked because ALLOW_LIVE_TRADING is False."
            )

        from alpaca_broker import AlpacaBroker

        return AlpacaBroker(paper_mode=paper_mode)

    raise ValueError(f"Broker not handled: {broker_name}")


def list_available_brokers():
    """
    Return broker availability information.

    This function intentionally does not import IBKR or Alpaca packages.
    It is safe for Streamlit dashboard startup.
    """

    return [
        {
            "broker": "paper",
            "status": "available",
            "description": "Internal simulated paper broker. No real trades."
        },
        {
            "broker": "ibkr",
            "status": "configured placeholder / local only",
            "description": "Interactive Brokers adapter. Use locally with TWS or IB Gateway."
        },
        {
            "broker": "alpaca",
            "status": "placeholder",
            "description": "Alpaca adapter planned. Not connected yet."
        }
    ]
