
from base_broker import BaseBroker
from ibkr_contracts import build_us_stock_contract, describe_contract
from ibkr_orders import build_order, describe_order


class IBKRBroker(BaseBroker):
    """
    Placeholder adapter for Interactive Brokers.

    This adapter is not connected yet.
    It exists so the platform can safely recognize IBKR as a future broker option.

    Current safe capabilities:
    - Build supported IBKR stock/ETF contracts
    - Build supported IBKR order objects
    - Describe contracts and orders

    It does not connect to IBKR yet.
    It does not submit orders yet.
    """

    def __init__(self, paper_mode=True):
        self.paper_mode = paper_mode
        self.configured = False

    # ==============================
    # Contract Builder Methods
    # ==============================

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

    # ==============================
    # Order Builder Methods
    # ==============================

    def build_ibkr_order(
        self,
        side,
        quantity,
        order_type="LMT",
        limit_price=None
    ):
        """
        Build a supported IBKR order object.
        This does not connect to IBKR and does not submit the order.
        """

        order = build_order(
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price
        )

        return order

    def describe_supported_order(
        self,
        side,
        quantity,
        order_type="LMT",
        limit_price=None
    ):
        """
        Return a readable order description.
        This does not connect to IBKR and does not submit the order.
        """

        order = self.build_ibkr_order(
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price
        )

        return describe_order(order)

    # ==============================
    # Not Yet Configured Methods
    # ==============================

    def _not_configured(self):
        raise NotImplementedError(
            "IBKR broker adapter is not configured for broker connection yet. "
            "Use PaperBroker for simulated trading. "
            "IBKR paper trading execution will be added in a later lesson."
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
