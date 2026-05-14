
from datetime import datetime
import uuid

import yfinance as yf

from base_broker import BaseBroker


class PaperBroker(BaseBroker):
    """
    Simulated broker for paper trading.

    This broker does not connect to any real broker.
    It does not place real trades.
    It only simulates account balance, positions, and orders.
    """

    def __init__(self, initial_cash=10000):
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.positions = {}
        self.orders = {}

    def get_account_info(self):
        total_position_value = 0

        for ticker, position in self.positions.items():
            latest_price = self.get_latest_price(ticker)
            total_position_value += position["quantity"] * latest_price

        equity = self.cash + total_position_value

        return {
            "cash": round(self.cash, 2),
            "equity": round(equity, 2),
            "initial_cash": round(self.initial_cash, 2),
            "open_positions": len(self.positions)
        }

    def get_positions(self):
        enriched_positions = []

        for ticker, position in self.positions.items():
            latest_price = self.get_latest_price(ticker)
            market_value = position["quantity"] * latest_price
            unrealized_pnl = market_value - position["cost_basis"]

            enriched_positions.append({
                "ticker": ticker,
                "quantity": position["quantity"],
                "average_price": round(position["average_price"], 2),
                "latest_price": round(latest_price, 2),
                "market_value": round(market_value, 2),
                "cost_basis": round(position["cost_basis"], 2),
                "unrealized_pnl": round(unrealized_pnl, 2)
            })

        return enriched_positions

    def get_latest_price(self, ticker):
        ticker = ticker.upper()

        data = yf.download(ticker, period="5d", progress=False)

        if data.empty:
            raise ValueError(f"No latest price data found for {ticker}")

        close_price = data["Close"]

        if hasattr(close_price, "iloc"):
            if len(close_price.shape) > 1:
                latest_price = close_price.iloc[-1, 0]
            else:
                latest_price = close_price.iloc[-1]
        else:
            latest_price = close_price

        return float(latest_price)

    def submit_order(self, ticker, side, quantity, order_type="market"):
        ticker = ticker.upper()
        side = side.lower()

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
                return order

            existing = self.positions[ticker]

            if quantity > existing["quantity"]:
                order["status"] = "rejected"
                order["reason"] = "Sell quantity exceeds paper position."
                self.orders[order_id] = order
                return order

            self.cash += order_value

            remaining_quantity = existing["quantity"] - quantity

            if remaining_quantity == 0:
                del self.positions[ticker]
            else:
                remaining_cost_basis = existing["average_price"] * remaining_quantity

                self.positions[ticker] = {
                    "quantity": remaining_quantity,
                    "average_price": existing["average_price"],
                    "cost_basis": remaining_cost_basis
                }

        self.orders[order_id] = order

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

        return order

    def get_order_status(self, order_id):
        if order_id not in self.orders:
            return {
                "order_id": order_id,
                "status": "not_found"
            }

        return self.orders[order_id]
