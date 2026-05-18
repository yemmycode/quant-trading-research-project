
from dataclasses import dataclass
from typing import List


@dataclass
class RiskCheckResult:
    approved: bool
    reason: str


class RiskManager:
    """
    Risk manager for checking whether a proposed trading action is safe.

    This class does not place trades.
    It only approves or blocks proposed actions.
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
        emergency_stop=False
    ):
        self.live_trading_enabled = live_trading_enabled
        self.require_manual_confirmation = require_manual_confirmation
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_weekly_loss = max_weekly_loss
        self.max_total_drawdown = max_total_drawdown
        self.allowed_tickers = allowed_tickers or []
        self.emergency_stop = emergency_stop

    def check_emergency_stop(self):
        if self.emergency_stop:
            return RiskCheckResult(
                approved=False,
                reason="Blocked: emergency stop is active."
            )

        return RiskCheckResult(
            approved=True,
            reason="Emergency stop check passed."
        )

    def check_live_trading_enabled(self):
        if not self.live_trading_enabled:
            return RiskCheckResult(
                approved=False,
                reason="Blocked: live trading is disabled in config."
            )

        return RiskCheckResult(
            approved=True,
            reason="Live trading enabled check passed."
        )

    def check_ticker_allowed(self, ticker):
        ticker = ticker.upper()

        if ticker not in self.allowed_tickers:
            return RiskCheckResult(
                approved=False,
                reason=f"Blocked: ticker {ticker} is not in allowed ticker list."
            )

        return RiskCheckResult(
            approved=True,
            reason=f"Ticker {ticker} is allowed."
        )

    def check_position_size(self, proposed_position_size):
        if proposed_position_size > self.max_position_size:
            return RiskCheckResult(
                approved=False,
                reason=(
                    f"Blocked: proposed position size {proposed_position_size:.2%} "
                    f"exceeds max allowed {self.max_position_size:.2%}."
                )
            )

        return RiskCheckResult(
            approved=True,
            reason="Position size check passed."
        )

    def check_daily_loss(self, current_daily_loss):
        if abs(current_daily_loss) > self.max_daily_loss:
            return RiskCheckResult(
                approved=False,
                reason=(
                    f"Blocked: current daily loss {current_daily_loss:.2%} "
                    f"exceeds max allowed {self.max_daily_loss:.2%}."
                )
            )

        return RiskCheckResult(
            approved=True,
            reason="Daily loss check passed."
        )

    def check_weekly_loss(self, current_weekly_loss):
        if abs(current_weekly_loss) > self.max_weekly_loss:
            return RiskCheckResult(
                approved=False,
                reason=(
                    f"Blocked: current weekly loss {current_weekly_loss:.2%} "
                    f"exceeds max allowed {self.max_weekly_loss:.2%}."
                )
            )

        return RiskCheckResult(
            approved=True,
            reason="Weekly loss check passed."
        )

    def check_total_drawdown(self, current_total_drawdown):
        if abs(current_total_drawdown) > self.max_total_drawdown:
            return RiskCheckResult(
                approved=False,
                reason=(
                    f"Blocked: current total drawdown {current_total_drawdown:.2%} "
                    f"exceeds max allowed {self.max_total_drawdown:.2%}."
                )
            )

        return RiskCheckResult(
            approved=True,
            reason="Total drawdown check passed."
        )

    def check_manual_confirmation(self, manual_confirmation_given=False):
        if self.require_manual_confirmation and not manual_confirmation_given:
            return RiskCheckResult(
                approved=False,
                reason="Blocked: manual confirmation is required but was not given."
            )

        return RiskCheckResult(
            approved=True,
            reason="Manual confirmation check passed."
        )

    def approve_order(
        self,
        ticker,
        proposed_position_size,
        current_daily_loss,
        current_weekly_loss,
        current_total_drawdown,
        manual_confirmation_given=False,
        live_order=False
    ):
        """
        Run all risk checks for a proposed order.

        live_order=False can be used for paper checks.
        live_order=True should require live trading to be enabled.
        """

        checks = []

        checks.append(self.check_emergency_stop())
        checks.append(self.check_ticker_allowed(ticker))
        checks.append(self.check_position_size(proposed_position_size))
        checks.append(self.check_daily_loss(current_daily_loss))
        checks.append(self.check_weekly_loss(current_weekly_loss))
        checks.append(self.check_total_drawdown(current_total_drawdown))
        checks.append(self.check_manual_confirmation(manual_confirmation_given))

        if live_order:
            checks.append(self.check_live_trading_enabled())

        failed_checks = [check for check in checks if not check.approved]

        if failed_checks:
            reasons = [check.reason for check in failed_checks]

            return RiskCheckResult(
                approved=False,
                reason=" | ".join(reasons)
            )

        return RiskCheckResult(
            approved=True,
            reason="Approved: all risk checks passed."
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
        emergency_stop=EMERGENCY_STOP
    )
