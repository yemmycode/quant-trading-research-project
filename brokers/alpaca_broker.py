
from base_broker import BaseBroker


class AlpacaBroker(BaseBroker):
    """
    Placeholder adapter for Alpaca.

    This adapter is not connected yet.
    It exists so the platform can safely recognize Alpaca as a future broker option.

    Future implementation may connect to:
    - Alpaca Paper Trading API
    - Alpaca Live Trading API, only after safety review
    """

    def __init__(self, paper_mode=True):
        self.paper_mode = paper_mode
        self.configured = False

    def _not_configured(self):
        raise NotImplementedError(
            "Alpaca broker adapter is not configured yet. "
            "Use PaperBroker for now. Alpaca paper trading integration may be added later."
        )

    def get_account_info(self):
        self._not_configured()

    def get_positions(self):
        self._not_configured()

    def get_latest_price(self, ticker):
        self._not_configured()

    def submit_order(self, ticker, side, quantity, order_type="market"):
        self._not_configured()

    def cancel_order(self, order_id):
        self._not_configured()

    def get_order_status(self, order_id):
        self._not_configured()
