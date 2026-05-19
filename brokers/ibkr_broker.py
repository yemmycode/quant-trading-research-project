
import sys
from pathlib import Path
import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())


from ib_insync import IB

from base_broker import BaseBroker
from ibkr_contracts import build_us_stock_contract, describe_contract
from ibkr_orders import build_order, describe_order


PROJECT_PATH = Path(__file__).resolve().parent.parent

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

from config import (
    IBKR_HOST,
    IBKR_PORT,
    IBKR_CLIENT_ID,
    IBKR_TRADING_MODE,
    IBKR_READ_ONLY,
    IBKR_ENABLE_ORDERS,
    EXECUTION_MODE,
    ALLOW_LIVE_TRADING,
    validate_ibkr_settings
)


class IBKRBroker(BaseBroker):
    """
    Interactive Brokers adapter.

    Current supported mode:
    - IBKR paper account connection
    - contract building
    - order object building
    - paper order submission only when safety settings allow it

    Live trading remains blocked unless explicitly enabled later.
    """

    def __init__(self, paper_mode=True):
        self.paper_mode = paper_mode
        self.ib = IB()

    # ==============================
    # Connection Methods
    # ==============================

    def connect(self):
        """
        Connect to IBKR TWS / IB Gateway.
        """

        validate_ibkr_settings()

        if not self.ib.isConnected():
            self.ib.connect(
                host=IBKR_HOST,
                port=IBKR_PORT,
                clientId=IBKR_CLIENT_ID,
                timeout=10
            )

        return self.ib.isConnected()

    def disconnect(self):
        """
        Disconnect safely from IBKR.
        """

        if self.ib.isConnected():
            self.ib.disconnect()

    def is_connected(self):
        return self.ib.isConnected()

    # ==============================
    # Safety Checks
    # ==============================

    def _ensure_paper_order_allowed(self):
        """
        Ensure order submission is allowed only for IBKR paper mode.
        """

        validate_ibkr_settings()

        if EXECUTION_MODE != "BROKER_PAPER":
            raise PermissionError(
                f"IBKR paper orders require EXECUTION_MODE='BROKER_PAPER'. "
                f"Current EXECUTION_MODE={EXECUTION_MODE}"
            )

        if IBKR_TRADING_MODE != "paper":
            raise PermissionError(
                f"IBKR_TRADING_MODE must be 'paper'. Current value: {IBKR_TRADING_MODE}"
            )

        if ALLOW_LIVE_TRADING:
            raise PermissionError(
                "ALLOW_LIVE_TRADING is True. Paper order test is blocked for safety."
            )

        if IBKR_READ_ONLY:
            raise PermissionError(
                "IBKR_READ_ONLY is True. Disable Read-Only API only for paper order testing."
            )

        if not IBKR_ENABLE_ORDERS:
            raise PermissionError(
                "IBKR_ENABLE_ORDERS is False. Set it to true only for IBKR paper order testing."
            )

    # ==============================
    # Contract Builder Methods
    # ==============================

    def build_contract(self, ticker):
        contract = build_us_stock_contract(ticker)
        return contract

    def describe_supported_contract(self, ticker):
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
        order = self.build_ibkr_order(
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price
        )

        return describe_order(order)

    # ==============================
    # Broker Interface Methods
    # ==============================

    def get_account_info(self):
        """
        Read basic account information from IBKR.
        """

        self.connect()

        accounts = self.ib.managedAccounts()

        if not accounts:
            return {
                "connected": True,
                "accounts": [],
                "message": "No managed accounts returned."
            }

        account_id = accounts[0]
        summary = self.ib.accountSummary(account=account_id)

        account_values = {}

        for item in summary:
            account_values[item.tag] = {
                "value": item.value,
                "currency": item.currency
            }

        return {
            "connected": True,
            "account_id": account_id,
            "values": account_values
        }

    def get_positions(self):
        """
        Read current positions from IBKR.
        """

        self.connect()

        positions = self.ib.positions()
        position_rows = []

        for position in positions:
            contract = position.contract

            position_rows.append({
                "account": position.account,
                "symbol": getattr(contract, "symbol", ""),
                "secType": getattr(contract, "secType", ""),
                "exchange": getattr(contract, "exchange", ""),
                "currency": getattr(contract, "currency", ""),
                "quantity": position.position,
                "average_cost": position.avgCost
            })

        return position_rows

    def get_latest_price(self, ticker):
        """
        Read delayed/latest market data from IBKR.
        """

        self.connect()

        contract = self.build_contract(ticker)
        qualified_contracts = self.ib.qualifyContracts(contract)

        if not qualified_contracts:
            raise ValueError(f"Could not qualify IBKR contract for {ticker}")

        contract = qualified_contracts[0]

        self.ib.reqMarketDataType(3)
        ticker_data = self.ib.reqMktData(contract, "", False, False)

        self.ib.sleep(5)

        price = ticker_data.marketPrice()

        if price is None or price != price or price <= 0:
            price = ticker_data.last

        if price is None or price != price or price <= 0:
            price = ticker_data.close

        if price is None or price != price or price <= 0:
            raise ValueError(f"No usable IBKR market price found for {ticker}")

        self.ib.cancelMktData(contract)

        return float(price)

    def submit_order(self, ticker, side, quantity, order_type="LMT", limit_price=None):
        """
        Submit an order to IBKR paper trading only.

        This is blocked unless:
        - EXECUTION_MODE = BROKER_PAPER
        - IBKR_TRADING_MODE = paper
        - IBKR_READ_ONLY = False
        - IBKR_ENABLE_ORDERS = True
        - ALLOW_LIVE_TRADING = False
        """

        self._ensure_paper_order_allowed()
        self.connect()

        contract = self.build_contract(ticker)

        qualified_contracts = self.ib.qualifyContracts(contract)

        if not qualified_contracts:
            raise ValueError(f"Could not qualify IBKR contract for {ticker}")

        contract = qualified_contracts[0]

        order = self.build_ibkr_order(
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price
        )

        trade = self.ib.placeOrder(contract, order)

        self.ib.sleep(3)

        return {
            "ticker": ticker,
            "contract": describe_contract(contract),
            "order": describe_order(order),
            "order_id": getattr(trade.order, "orderId", None),
            "order_status": getattr(trade.orderStatus, "status", None),
            "filled": getattr(trade.orderStatus, "filled", None),
            "remaining": getattr(trade.orderStatus, "remaining", None),
            "avg_fill_price": getattr(trade.orderStatus, "avgFillPrice", None),
            "message": "IBKR paper order submitted. Check TWS paper account/order panel."
        }

    def get_open_orders(self):
        """
        Return currently open IBKR paper orders.
        """

        self.connect()

        open_trades = self.ib.openTrades()

        rows = []

        for trade in open_trades:
            contract = trade.contract
            order = trade.order
            status = trade.orderStatus

            rows.append({
                "order_id": getattr(order, "orderId", None),
                "perm_id": getattr(order, "permId", None),
                "symbol": getattr(contract, "symbol", None),
                "sec_type": getattr(contract, "secType", None),
                "exchange": getattr(contract, "exchange", None),
                "currency": getattr(contract, "currency", None),
                "action": getattr(order, "action", None),
                "order_type": getattr(order, "orderType", None),
                "quantity": getattr(order, "totalQuantity", None),
                "limit_price": getattr(order, "lmtPrice", None),
                "status": getattr(status, "status", None),
                "filled": getattr(status, "filled", None),
                "remaining": getattr(status, "remaining", None),
                "avg_fill_price": getattr(status, "avgFillPrice", None)
            })

        return rows

    def get_all_trades(self):
        """
        Return known IBKR trades for the current API session.
        """

        self.connect()

        trades = self.ib.trades()

        rows = []

        for trade in trades:
            contract = trade.contract
            order = trade.order
            status = trade.orderStatus

            rows.append({
                "order_id": getattr(order, "orderId", None),
                "perm_id": getattr(order, "permId", None),
                "symbol": getattr(contract, "symbol", None),
                "sec_type": getattr(contract, "secType", None),
                "exchange": getattr(contract, "exchange", None),
                "currency": getattr(contract, "currency", None),
                "action": getattr(order, "action", None),
                "order_type": getattr(order, "orderType", None),
                "quantity": getattr(order, "totalQuantity", None),
                "limit_price": getattr(order, "lmtPrice", None),
                "status": getattr(status, "status", None),
                "filled": getattr(status, "filled", None),
                "remaining": getattr(status, "remaining", None),
                "avg_fill_price": getattr(status, "avgFillPrice", None)
            })

        return rows

    def get_order_status(self, order_id):
        """
        Find a specific IBKR paper order status by order ID.
        """

        self.connect()

        order_id = int(order_id)

        trades = self.ib.trades()
        open_trades = self.ib.openTrades()

        all_trades = list(trades) + list(open_trades)

        for trade in all_trades:
            order = trade.order
            status = trade.orderStatus
            contract = trade.contract

            if getattr(order, "orderId", None) == order_id:
                return {
                    "found": True,
                    "order_id": getattr(order, "orderId", None),
                    "perm_id": getattr(order, "permId", None),
                    "symbol": getattr(contract, "symbol", None),
                    "action": getattr(order, "action", None),
                    "order_type": getattr(order, "orderType", None),
                    "quantity": getattr(order, "totalQuantity", None),
                    "limit_price": getattr(order, "lmtPrice", None),
                    "status": getattr(status, "status", None),
                    "filled": getattr(status, "filled", None),
                    "remaining": getattr(status, "remaining", None),
                    "avg_fill_price": getattr(status, "avgFillPrice", None)
                }

        return {
            "found": False,
            "order_id": order_id,
            "message": "Order ID was not found in current IBKR API session trades/open trades."
        }

    def cancel_order(self, order_id):
        """
        Cancel an open IBKR paper order by order ID.

        This only works for open orders visible in the current IBKR session.
        """

        self._ensure_paper_order_allowed()
        self.connect()

        order_id = int(order_id)

        open_trades = self.ib.openTrades()

        for trade in open_trades:
            order = trade.order
            contract = trade.contract
            status = trade.orderStatus

            if getattr(order, "orderId", None) == order_id:
                self.ib.cancelOrder(order)
                self.ib.sleep(2)

                return {
                    "cancel_requested": True,
                    "order_id": getattr(order, "orderId", None),
                    "symbol": getattr(contract, "symbol", None),
                    "action": getattr(order, "action", None),
                    "order_type": getattr(order, "orderType", None),
                    "quantity": getattr(order, "totalQuantity", None),
                    "limit_price": getattr(order, "lmtPrice", None),
                    "previous_status": getattr(status, "status", None),
                    "message": "Cancel request sent to IBKR paper account."
                }

        return {
            "cancel_requested": False,
            "order_id": order_id,
            "message": "No open order found with this order ID."
        }
