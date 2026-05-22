
from datetime import datetime
import uuid
import sys
from pathlib import Path

import yfinance as yf

from base_broker import BaseBroker


PROJECT_PATH = Path(__file__).resolve().parent.parent

if str(PROJECT_PATH) not in sys.path:
    sys.path.append(str(PROJECT_PATH))

from database import save_paper_broker_state, load_paper_broker_state


class PaperBroker(BaseBroker):
    """
    Simulated broker for paper trading.

    This broker does not connect to any real broker.
    It does not place real trades.

    It can persist simulated cash, positions, and orders to SQLite.
    """

    def __init__(self, initial_cash=10000, use_database=True):
        self.use_database = use_database

        if self.use_database:
            saved_state = load_paper_broker_state(default_initial_cash=initial_cash)

            self.initial_cash = float(saved_state["initial_cash"])
            self.cash = float(saved_state["cash"])
            self.positions = saved_state["positions"]
            self.orders = saved_state["orders"]

        else:
            self.initial_cash = float(initial_cash)
            self.cash = float(initial_cash)
            self.positions = {}
            self.orders = {}

    def save_state(self):
        """
        Save paper broker state to SQLite.
        """

        if self.use_database:
            save_paper_broker_state(
                initial_cash=self.initial_cash,
                cash=self.cash,
                positions=self.positions,
                orders=self.orders
            )

    def get_account_info(self):
        """
        Return safe simulated account information.

        This version does not crash when a latest price is missing.
        It falls back to average entry price and records a warning.
        """

        total_market_value = 0.0
        total_unrealized_pnl = 0.0
        open_positions = []
        price_warnings = []

        positions_dict = getattr(self, "positions", {})

        if positions_dict is None:
            positions_dict = {}

        for ticker, position in positions_dict.items():
            if not isinstance(position, dict):
                continue

            try:
                quantity = float(position.get("quantity", 0) or 0)
            except Exception:
                quantity = 0.0

            try:
                avg_price = float(
                    position.get("avg_price")
                    or position.get("average_price")
                    or position.get("entry_price")
                    or position.get("avg_entry_price")
                    or 0.0
                )
            except Exception:
                avg_price = 0.0

            latest_price = self.get_latest_price(ticker)

            if latest_price is None:
                latest_price = avg_price

                price_warnings.append(
                    f"No latest market price found for {ticker}. "
                    "Using average entry price as fallback."
                )

            market_value = quantity * latest_price
            unrealized_pnl = (latest_price - avg_price) * quantity

            total_market_value += market_value
            total_unrealized_pnl += unrealized_pnl

            open_positions.append({
                "ticker": ticker,
                "quantity": quantity,
                "avg_price": avg_price,
                "latest_price": latest_price,
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl,
            })

        cash_value = getattr(self, "cash", None)

        if cash_value is None:
            cash_value = getattr(self, "cash_balance", 0.0)

        try:
            cash_balance = float(cash_value)
        except Exception:
            cash_balance = 0.0

        total_equity = cash_balance + total_market_value

        initial_cash_value = getattr(self, "initial_cash", None)

        if initial_cash_value is None:
            initial_cash_value = getattr(self, "starting_cash", None)

        if initial_cash_value is None:
            initial_cash_value = cash_balance + sum([
                position.get("avg_price", 0.0) * position.get("quantity", 0.0)
                for position in open_positions
            ])

        try:
            initial_cash_value = float(initial_cash_value)
        except Exception:
            initial_cash_value = 0.0

        return {
            "initial_cash": initial_cash_value,
            "starting_cash": initial_cash_value,
            "cash_balance": cash_balance,
            "cash": cash_balance,
            "total_market_value": total_market_value,
            "market_value": total_market_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "unrealized_pnl": total_unrealized_pnl,
            "total_equity": total_equity,
            "equity": total_equity,
            "open_positions": open_positions,
            "positions": open_positions,
            "price_warnings": price_warnings,
        }
    def get_positions(self):
        enriched_positions = []

        for ticker, position in self.positions.items():
            latest_price = self.get_latest_price(ticker)
            market_value = position["quantity"] * latest_price
            unrealized_pnl = market_value - position["cost_basis"]

            enriched_positions.append({
                "ticker": ticker,
                "quantity": round(position["quantity"], 6),
                "average_price": round(position["average_price"], 2),
                "latest_price": round(latest_price, 2),
                "market_value": round(market_value, 2),
                "cost_basis": round(position["cost_basis"], 2),
                "unrealized_pnl": round(unrealized_pnl, 2)
            })

        return enriched_positions

    def get_latest_price(self, ticker):
        """
        Return the latest known price for a ticker.

        Safe fallback order:
        1. Latest cached market price
        2. Average entry price from open position
        3. None

        This prevents the dashboard from crashing when positions exist
        but no fresh price has been loaded after restart/deployment.
        """

        ticker = str(ticker).upper().strip()

        # Try common latest price dictionaries first
        for attr_name in ["latest_prices", "market_data", "prices"]:
            price_store = getattr(self, attr_name, None)

            if isinstance(price_store, dict):
                price = price_store.get(ticker)

                if price is not None:
                    try:
                        return float(price)
                    except Exception:
                        pass

        # Fallback to position average price if available
        positions_dict = getattr(self, "positions", {})

        if isinstance(positions_dict, dict):
            position = positions_dict.get(ticker)

            if isinstance(position, dict):
                avg_price = (
                    position.get("avg_price")
                    or position.get("average_price")
                    or position.get("entry_price")
                    or position.get("avg_entry_price")
                )

                if avg_price is not None:
                    try:
                        return float(avg_price)
                    except Exception:
                        pass

        return None
    def submit_order(self, ticker, side, quantity, order_type="market"):
        ticker = ticker.upper()
        side = side.lower()
        quantity = float(quantity)

        if side not in ["buy", "sell"]:
            raise ValueError("side must be either 'buy' or 'sell'.")

        if quantity <= 0:
            raise ValueError("quantity must be greater than zero.")

        latest_price = self.get_latest_price(ticker)
        order_value = latest_price * quantity

        order_id = str(uuid.uuid4())

        order = {
            "order_id": order_id,
            "ticker": ticker,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "price": latest_price,
            "order_value": order_value,
            "status": "filled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if side == "buy":
            if order_value > self.cash:
                order["status"] = "rejected"
                order["reason"] = "Insufficient paper cash."
                self.orders[order_id] = order
                self.save_state()
                return order

            self.cash -= order_value

            if ticker in self.positions:
                existing = self.positions[ticker]

                new_quantity = existing["quantity"] + quantity
                new_cost_basis = existing["cost_basis"] + order_value
                new_average_price = new_cost_basis / new_quantity

                self.positions[ticker] = {
                    "quantity": new_quantity,
                    "average_price": new_average_price,
                    "cost_basis": new_cost_basis
                }
            else:
                self.positions[ticker] = {
                    "quantity": quantity,
                    "average_price": latest_price,
                    "cost_basis": order_value
                }

        elif side == "sell":
            if ticker not in self.positions:
                order["status"] = "rejected"
                order["reason"] = "No paper position to sell."
                self.orders[order_id] = order
                self.save_state()
                return order

            existing = self.positions[ticker]

            if quantity > existing["quantity"]:
                order["status"] = "rejected"
                order["reason"] = "Sell quantity exceeds paper position."
                self.orders[order_id] = order
                self.save_state()
                return order

            self.cash += order_value

            remaining_quantity = existing["quantity"] - quantity

            if remaining_quantity <= 0:
                del self.positions[ticker]
            else:
                remaining_cost_basis = existing["average_price"] * remaining_quantity

                self.positions[ticker] = {
                    "quantity": remaining_quantity,
                    "average_price": existing["average_price"],
                    "cost_basis": remaining_cost_basis
                }

        self.orders[order_id] = order
        self.save_state()

        return order

    def cancel_order(self, order_id):
        if order_id not in self.orders:
            return {
                "order_id": order_id,
                "status": "not_found",
                "message": "Order not found."
            }

        order = self.orders[order_id]

        if order["status"] == "filled":
            return {
                "order_id": order_id,
                "status": "cannot_cancel",
                "message": "Filled paper orders cannot be cancelled."
            }

        order["status"] = "cancelled"
        self.orders[order_id] = order
        self.save_state()

        return order

    def get_order_status(self, order_id):
        if order_id not in self.orders:
            return {
                "order_id": order_id,
                "status": "not_found"
            }

        return self.orders[order_id]
