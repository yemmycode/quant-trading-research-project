
from base_broker import BaseBroker
from ibkr_contracts import build_us_stock_contract, describe_contract


class IBKRBroker(BaseBroker):
    """
    Placeholder adapter for Interactive Brokers.

    This adapter is not connected yet.
    It exists so the platform can safely recognize IBKR as a future broker option.

    Future implementation will connect to:
    - IBKR Trader Workstation
    - IB Gateway
    - IBKR Paper Trading
    """

    def __init__(self, paper_mode=True):
        self.paper_mode = paper_mode
        self.configured = False


    def build_contract(self, ticker):
        """
        Build a supported IBKR contract for a ticker.
        This does not connect to IBKR.
        """

        contract = build_us_stock_contract(ticker)
        return contract

    def describe_supported_contract(self, ticker):
        """
        Return a readable contract description for a supported ticker.
        """

        contract = self.build_contract(ticker)
        return describe_contract(contract)

    def _not_configured(self):
        raise NotImplementedError(
            "IBKR broker adapter is not configured yet. "
            "Use PaperBroker for now. IBKR paper trading integration will be added in a later lesson."
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
