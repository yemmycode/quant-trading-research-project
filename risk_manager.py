
from dataclasses import dataclass


@dataclass
class RiskCheckResult:
    approved: bool
    reason: str
    details: dict


class RiskManager:
    """
    Central risk manager for simulated, broker-paper, and future live trading.

    The purpose of this class is to block unsafe orders before they reach any broker.
    """

    def __init__(
        self,
        live_trading_enabled=False,
        require_manual_confirmation=True,
        max_position_size=0.10,
        max_daily_loss=0.02,
        max_weekly_loss=0.05,
        max_total_drawdown=0.10,
        allowed_tickers=None,
        emergency_stop=False,
        allowed_sides=None,
        allowed_asset_types=None,
        allow_short_selling=False,
        allow_margin=False,
        max_order_quantity=None,
        max_order_value=None,
        execution_mode="BACKTEST",
        default_broker="paper"
    ):
        self.live_trading_enabled = live_trading_enabled
        self.require_manual_confirmation = require_manual_confirmation
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_weekly_loss = max_weekly_loss
        self.max_total_drawdown = max_total_drawdown
        self.allowed_tickers = allowed_tickers or ["SPY", "QQQ"]
        self.emergency_stop = emergency_stop

        self.allowed_sides = allowed_sides or ["BUY", "SELL"]
        self.allowed_asset_types = allowed_asset_types or ["stock", "etf"]
        self.allow_short_selling = allow_short_selling
        self.allow_margin = allow_margin
        self.max_order_quantity = max_order_quantity
        self.max_order_value = max_order_value

        self.execution_mode = execution_mode
        self.default_broker = default_broker

    # ==============================
    # Helpers
    # ==============================

    def _normalize_ticker(self, ticker):
        if ticker is None:
            return ""

        return str(ticker).strip().upper()

    def _normalize_side(self, side):
        if side is None:
            return ""

        return str(side).strip().upper()

    def _normalize_asset_type(self, asset_type):
        if asset_type is None:
            return "stock"

        return str(asset_type).strip().lower()

    def _block(self, reason, details=None):
        return RiskCheckResult(
            approved=False,
            reason=reason,
            details=details or {}
        )

    def _approve(self, reason="Approved.", details=None):
        return RiskCheckResult(
            approved=True,
            reason=reason,
            details=details or {}
        )

    # ==============================
    # General Order Approval
    # ==============================

    def approve_order(
        self,
        ticker,
        proposed_position_size,
        current_daily_loss=0.0,
        current_weekly_loss=0.0,
        current_total_drawdown=0.0,
        manual_confirmation_given=False,
        live_order=False
    ):
        """
        Backward-compatible simple risk check.
        """

        ticker = self._normalize_ticker(ticker)

        if self.emergency_stop:
            return self._block(
                "Blocked: emergency stop is active.",
                {"ticker": ticker}
            )

        if live_order and not self.live_trading_enabled:
            return self._block(
                "Blocked: live trading is disabled in config.",
                {"ticker": ticker, "live_order": live_order}
            )

        if ticker not in self.allowed_tickers:
            return self._block(
                f"Blocked: ticker {ticker} is not in allowed ticker list.",
                {"ticker": ticker, "allowed_tickers": self.allowed_tickers}
            )

        if proposed_position_size <= 0:
            return self._block(
                "Blocked: proposed position size must be greater than zero.",
                {"proposed_position_size": proposed_position_size}
            )

        if proposed_position_size > self.max_position_size:
            return self._block(
                "Blocked: proposed position size exceeds max allowed position size.",
                {
                    "proposed_position_size": proposed_position_size,
                    "max_position_size": self.max_position_size
                }
            )

        if current_daily_loss <= -abs(self.max_daily_loss):
            return self._block(
                "Blocked: daily loss limit reached.",
                {
                    "current_daily_loss": current_daily_loss,
                    "max_daily_loss": self.max_daily_loss
                }
            )

        if current_weekly_loss <= -abs(self.max_weekly_loss):
            return self._block(
                "Blocked: weekly loss limit reached.",
                {
                    "current_weekly_loss": current_weekly_loss,
                    "max_weekly_loss": self.max_weekly_loss
                }
            )

        if current_total_drawdown <= -abs(self.max_total_drawdown):
            return self._block(
                "Blocked: total drawdown limit reached.",
                {
                    "current_total_drawdown": current_total_drawdown,
                    "max_total_drawdown": self.max_total_drawdown
                }
            )

        if self.require_manual_confirmation and not manual_confirmation_given:
            return self._block(
                "Blocked: manual confirmation is required.",
                {"manual_confirmation_given": manual_confirmation_given}
            )

        return self._approve(
            "Approved: simple risk checks passed.",
            {
                "ticker": ticker,
                "proposed_position_size": proposed_position_size,
                "live_order": live_order
            }
        )

    # ==============================
    # Broker Order Approval
    # ==============================

    def approve_broker_order(
        self,
        ticker,
        side,
        quantity,
        order_type,
        asset_type="stock",
        proposed_position_size=None,
        estimated_price=None,
        estimated_order_value=None,
        current_position_quantity=0,
        current_daily_loss=0.0,
        current_weekly_loss=0.0,
        current_total_drawdown=0.0,
        manual_confirmation_given=False,
        broker_name=None,
        execution_mode=None,
        live_order=False
    ):
        """
        Stronger broker-specific approval check.

        This should be used before IBKR paper/live order submission.
        """

        ticker = self._normalize_ticker(ticker)
        side = self._normalize_side(side)
        asset_type = self._normalize_asset_type(asset_type)

        broker_name = broker_name or self.default_broker
        execution_mode = execution_mode or self.execution_mode

        details = {
            "ticker": ticker,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "asset_type": asset_type,
            "proposed_position_size": proposed_position_size,
            "estimated_price": estimated_price,
            "estimated_order_value": estimated_order_value,
            "current_position_quantity": current_position_quantity,
            "broker_name": broker_name,
            "execution_mode": execution_mode,
            "live_order": live_order
        }

        if self.emergency_stop:
            return self._block("Blocked: emergency stop is active.", details)

        if execution_mode not in ["BROKER_PAPER", "LIVE_MANUAL"]:
            return self._block(
                "Blocked: broker orders require BROKER_PAPER or LIVE_MANUAL execution mode.",
                details
            )

        if live_order and execution_mode != "LIVE_MANUAL":
            return self._block(
                "Blocked: live_order=True requires LIVE_MANUAL execution mode.",
                details
            )

        if live_order and not self.live_trading_enabled:
            return self._block(
                "Blocked: live trading is disabled.",
                details
            )

        if ticker not in self.allowed_tickers:
            return self._block(
                f"Blocked: ticker {ticker} is not allowed.",
                {
                    **details,
                    "allowed_tickers": self.allowed_tickers
                }
            )

        if side not in self.allowed_sides:
            return self._block(
                f"Blocked: side {side} is not allowed.",
                {
                    **details,
                    "allowed_sides": self.allowed_sides
                }
            )

        if asset_type not in self.allowed_asset_types:
            return self._block(
                f"Blocked: asset type {asset_type} is not allowed.",
                {
                    **details,
                    "allowed_asset_types": self.allowed_asset_types
                }
            )

        try:
            quantity = float(quantity)
        except Exception:
            return self._block("Blocked: quantity must be numeric.", details)

        if quantity <= 0:
            return self._block("Blocked: quantity must be greater than zero.", details)

        if self.max_order_quantity is not None and quantity > self.max_order_quantity:
            return self._block(
                "Blocked: quantity exceeds max order quantity.",
                {
                    **details,
                    "quantity": quantity,
                    "max_order_quantity": self.max_order_quantity
                }
            )

        if side == "SELL" and not self.allow_short_selling:
            if float(current_position_quantity) <= 0:
                return self._block(
                    "Blocked: short selling is disabled and there is no existing position to sell.",
                    details
                )

            if quantity > float(current_position_quantity):
                return self._block(
                    "Blocked: sell quantity exceeds current position and short selling is disabled.",
                    {
                        **details,
                        "quantity": quantity,
                        "current_position_quantity": current_position_quantity
                    }
                )

        if proposed_position_size is not None:
            try:
                proposed_position_size = float(proposed_position_size)
            except Exception:
                return self._block(
                    "Blocked: proposed position size must be numeric.",
                    details
                )

            if proposed_position_size <= 0:
                return self._block(
                    "Blocked: proposed position size must be greater than zero.",
                    details
                )

            if proposed_position_size > self.max_position_size:
                return self._block(
                    "Blocked: proposed position size exceeds max allowed position size.",
                    {
                        **details,
                        "proposed_position_size": proposed_position_size,
                        "max_position_size": self.max_position_size
                    }
                )

        if estimated_order_value is not None:
            try:
                estimated_order_value = float(estimated_order_value)
            except Exception:
                return self._block(
                    "Blocked: estimated order value must be numeric.",
                    details
                )

            if estimated_order_value <= 0:
                return self._block(
                    "Blocked: estimated order value must be greater than zero.",
                    details
                )

            if self.max_order_value is not None and estimated_order_value > self.max_order_value:
                return self._block(
                    "Blocked: estimated order value exceeds max order value.",
                    {
                        **details,
                        "estimated_order_value": estimated_order_value,
                        "max_order_value": self.max_order_value
                    }
                )

        if current_daily_loss <= -abs(self.max_daily_loss):
            return self._block("Blocked: daily loss limit reached.", details)

        if current_weekly_loss <= -abs(self.max_weekly_loss):
            return self._block("Blocked: weekly loss limit reached.", details)

        if current_total_drawdown <= -abs(self.max_total_drawdown):
            return self._block("Blocked: total drawdown limit reached.", details)

        if self.require_manual_confirmation and not manual_confirmation_given:
            return self._block(
                "Blocked: manual confirmation is required before broker order.",
                details
            )

        if broker_name == "ibkr" and execution_mode == "BROKER_PAPER":
            return self._approve(
                "Approved: IBKR paper broker order passed risk checks.",
                details
            )

        if broker_name == "ibkr" and execution_mode == "LIVE_MANUAL":
            if not self.live_trading_enabled:
                return self._block(
                    "Blocked: IBKR live manual trading is disabled.",
                    details
                )

            return self._approve(
                "Approved: IBKR live manual order passed risk checks.",
                details
            )

        return self._approve(
            "Approved: broker order passed risk checks.",
            details
        )


def create_risk_manager_from_config():
    """
    Create a RiskManager using settings from config.py.
    """

    from config import (
        LIVE_TRADING_ENABLED,
        REQUIRE_MANUAL_CONFIRMATION,
        MAX_POSITION_SIZE,
        MAX_DAILY_LOSS,
        MAX_WEEKLY_LOSS,
        MAX_TOTAL_DRAWDOWN,
        ALLOWED_TICKERS,
        EMERGENCY_STOP,
        EXECUTION_MODE,
        DEFAULT_BROKER,
        ALLOW_LIVE_TRADING,
        validate_execution_settings
    )

    validate_execution_settings()

    effective_live_trading_enabled = (
        LIVE_TRADING_ENABLED
        and ALLOW_LIVE_TRADING
        and EXECUTION_MODE == "LIVE_MANUAL"
    )

    return RiskManager(
        live_trading_enabled=effective_live_trading_enabled,
        require_manual_confirmation=REQUIRE_MANUAL_CONFIRMATION,
        max_position_size=MAX_POSITION_SIZE,
        max_daily_loss=MAX_DAILY_LOSS,
        max_weekly_loss=MAX_WEEKLY_LOSS,
        max_total_drawdown=MAX_TOTAL_DRAWDOWN,
        allowed_tickers=ALLOWED_TICKERS,
        emergency_stop=EMERGENCY_STOP,
        allowed_sides=["BUY", "SELL"],
        allowed_asset_types=["stock", "etf"],
        allow_short_selling=False,
        allow_margin=False,
        max_order_quantity=None,
        max_order_value=None,
        execution_mode=EXECUTION_MODE,
        default_broker=DEFAULT_BROKER
    )
