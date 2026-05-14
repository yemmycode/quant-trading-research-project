
from pathlib import Path
from datetime import datetime
import pandas as pd

from database import save_order_log


class OrderManager:
    """
    Order Manager controls the flow between:
    - strategy signals
    - risk manager
    - broker adapter

    It does not generate trading signals.
    It only validates and submits approved orders.
    """

    def __init__(
        self,
        broker,
        risk_manager,
        results_path=None
    ):
        self.broker = broker
        self.risk_manager = risk_manager

        if results_path is None:
            self.results_path = Path("results")
        else:
            self.results_path = Path(results_path)

        self.results_path.mkdir(parents=True, exist_ok=True)

        self.order_log_file = self.results_path / "order_log.csv"

    def calculate_quantity_from_position_size(
        self,
        ticker,
        position_size,
        account_equity
    ):
        """
        Calculate how many shares to buy based on position size and account equity.
        """

        latest_price = self.broker.get_latest_price(ticker)

        capital_to_allocate = account_equity * position_size

        quantity = int(capital_to_allocate // latest_price)

        return quantity, latest_price, capital_to_allocate

    def append_order_log(self, log_row):
        """
        Append order result to order_log.csv.
        """

        log_df = pd.DataFrame([log_row])

        if self.order_log_file.exists():
            existing_log = pd.read_csv(self.order_log_file)
            updated_log = pd.concat([existing_log, log_df], ignore_index=True)
        else:
            updated_log = log_df

        updated_log.to_csv(self.order_log_file, index=False)

        save_order_log(log_df)

        return self.order_log_file

    def submit_managed_order(
        self,
        ticker,
        side,
        proposed_position_size,
        current_daily_loss=0.00,
        current_weekly_loss=0.00,
        current_total_drawdown=0.00,
        manual_confirmation_given=False,
        live_order=False,
        quantity=None
    ):
        """
        Submit an order only if risk checks approve it.

        If quantity is not provided, the order manager calculates quantity
        from proposed_position_size and account equity.
        """

        ticker = ticker.upper()
        side = side.lower()

        account_info = self.broker.get_account_info()
        account_equity = account_info["equity"]

        risk_result = self.risk_manager.approve_order(
            ticker=ticker,
            proposed_position_size=proposed_position_size,
            current_daily_loss=current_daily_loss,
            current_weekly_loss=current_weekly_loss,
            current_total_drawdown=current_total_drawdown,
            manual_confirmation_given=manual_confirmation_given,
            live_order=live_order
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not risk_result.approved:
            log_row = {
                "Timestamp": timestamp,
                "Ticker": ticker,
                "Side": side,
                "Requested Position Size": proposed_position_size,
                "Quantity": quantity,
                "Status": "blocked",
                "Reason": risk_result.reason,
                "Live Order": live_order,
                "Account Equity": account_equity
            }

            self.append_order_log(log_row)

            return {
                "approved": False,
                "status": "blocked",
                "reason": risk_result.reason,
                "order": None
            }

        if quantity is None:
            quantity, latest_price, capital_to_allocate = self.calculate_quantity_from_position_size(
                ticker=ticker,
                position_size=proposed_position_size,
                account_equity=account_equity
            )
        else:
            latest_price = self.broker.get_latest_price(ticker)
            capital_to_allocate = quantity * latest_price

        if quantity <= 0:
            reason = "Calculated quantity is zero. Position size may be too small for this asset price."

            log_row = {
                "Timestamp": timestamp,
                "Ticker": ticker,
                "Side": side,
                "Requested Position Size": proposed_position_size,
                "Quantity": quantity,
                "Status": "blocked",
                "Reason": reason,
                "Live Order": live_order,
                "Account Equity": account_equity
            }

            self.append_order_log(log_row)

            return {
                "approved": False,
                "status": "blocked",
                "reason": reason,
                "order": None
            }

        order = self.broker.submit_order(
            ticker=ticker,
            side=side,
            quantity=quantity,
            order_type="market"
        )

        log_row = {
            "Timestamp": timestamp,
            "Ticker": ticker,
            "Side": side,
            "Requested Position Size": proposed_position_size,
            "Quantity": quantity,
            "Estimated Price": latest_price,
            "Estimated Capital": capital_to_allocate,
            "Status": order.get("status"),
            "Reason": order.get("reason", "Order submitted to broker adapter."),
            "Live Order": live_order,
            "Account Equity": account_equity,
            "Order ID": order.get("order_id")
        }

        self.append_order_log(log_row)

        return {
            "approved": True,
            "status": order.get("status"),
            "reason": log_row["Reason"],
            "order": order
        }
