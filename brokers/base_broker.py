
from abc import ABC, abstractmethod


class BaseBroker(ABC):
    """
    Abstract base class for broker adapters.

    Every broker adapter should follow this structure.
    This helps us later plug in different brokers such as:
    - PaperBroker
    - AlpacaBroker
    - InteractiveBrokersAdapter
    - SaxoBrokerAdapter
    """

    @abstractmethod
    def get_account_info(self):
        """
        Return account information such as cash, equity, and buying power.
        """
        pass

    @abstractmethod
    def get_positions(self):
        """
        Return current open positions.
        """
        pass

    @abstractmethod
    def get_latest_price(self, ticker):
        """
        Return latest available price for a ticker.
        """
        pass

    @abstractmethod
    def submit_order(self, ticker, side, quantity, order_type="market"):
        """
        Submit an order.

        side should be:
        - buy
        - sell

        order_type can later support:
        - market
        - limit
        - stop
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id):
        """
        Cancel an existing order.
        """
        pass

    @abstractmethod
    def get_order_status(self, order_id):
        """
        Return the status of an order.
        """
        pass
