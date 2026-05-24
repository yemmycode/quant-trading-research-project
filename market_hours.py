
"""
Market Hours Awareness

This module checks whether a market is open before signal/order workflows proceed.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd


US_EASTERN = ZoneInfo("America/New_York")
SOUTH_AFRICA = ZoneInfo("Africa/Johannesburg")


def get_now_times():
    """
    Return current timestamps in UTC, US Eastern, and South Africa time.
    """

    now_utc = datetime.now(ZoneInfo("UTC"))
    now_et = now_utc.astimezone(US_EASTERN)
    now_sast = now_utc.astimezone(SOUTH_AFRICA)

    return {
        "utc": now_utc,
        "us_eastern": now_et,
        "south_africa": now_sast,
        "utc_text": now_utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "us_eastern_text": now_et.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "south_africa_text": now_sast.strftime("%Y-%m-%d %H:%M:%S %Z"),
    }


def get_us_market_calendar():
    """
    Return NYSE market calendar.

    Falls back safely if pandas_market_calendars is unavailable.
    """

    try:
        import pandas_market_calendars as mcal
        return mcal.get_calendar("NYSE")
    except Exception:
        return None


def basic_weekday_market_check(now_et=None):
    """
    Simple fallback market check.

    This does not account for US holidays or special half-days.
    It is only used if pandas_market_calendars is unavailable.
    """

    if now_et is None:
        now_et = datetime.now(US_EASTERN)

    is_weekday = now_et.weekday() < 5

    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

    is_regular_hours = is_weekday and market_open <= now_et <= market_close

    if not is_weekday:
        session_status = "closed_weekend"
    elif now_et < market_open:
        session_status = "pre_market"
    elif market_open <= now_et <= market_close:
        session_status = "regular_market_open"
    else:
        session_status = "after_hours"

    return {
        "calendar_available": False,
        "market": "US",
        "exchange": "NYSE",
        "is_open": bool(is_regular_hours),
        "session_status": session_status,
        "now_et": now_et.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "market_open_et": market_open.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "market_close_et": market_close.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "warning": "Fallback check used. US holidays and special half-days are not included.",
    }


def check_us_market_hours(now=None):
    """
    Check whether US regular market session is currently open.

    Uses NYSE calendar when available.
    """

    if now is None:
        now_utc = datetime.now(ZoneInfo("UTC"))
    else:
        if now.tzinfo is None:
            now_utc = now.replace(tzinfo=ZoneInfo("UTC"))
        else:
            now_utc = now.astimezone(ZoneInfo("UTC"))

    now_et = now_utc.astimezone(US_EASTERN)

    calendar = get_us_market_calendar()

    if calendar is None:
        return basic_weekday_market_check(now_et=now_et)

    start_date = (now_et.date() - timedelta(days=3)).isoformat()
    end_date = (now_et.date() + timedelta(days=3)).isoformat()

    schedule = calendar.schedule(start_date=start_date, end_date=end_date)

    if schedule.empty:
        return {
            "calendar_available": True,
            "market": "US",
            "exchange": "NYSE",
            "is_open": False,
            "session_status": "closed_no_schedule",
            "now_et": now_et.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "market_open_et": None,
            "market_close_et": None,
            "warning": "No NYSE schedule found for this date range.",
        }

    today_str = now_et.date().isoformat()

    today_schedule = schedule[schedule.index.strftime("%Y-%m-%d") == today_str]

    if today_schedule.empty:
        next_open_text = None

        future_schedule = schedule[schedule.index.strftime("%Y-%m-%d") > today_str]

        if not future_schedule.empty:
            next_open = future_schedule.iloc[0]["market_open"].to_pydatetime().astimezone(US_EASTERN)
            next_open_text = next_open.strftime("%Y-%m-%d %H:%M:%S %Z")

        return {
            "calendar_available": True,
            "market": "US",
            "exchange": "NYSE",
            "is_open": False,
            "session_status": "closed_no_trading_day",
            "now_et": now_et.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "market_open_et": None,
            "market_close_et": None,
            "next_open_et": next_open_text,
            "warning": "",
        }

    market_open = today_schedule.iloc[0]["market_open"].to_pydatetime().astimezone(US_EASTERN)
    market_close = today_schedule.iloc[0]["market_close"].to_pydatetime().astimezone(US_EASTERN)

    if now_et < market_open:
        session_status = "pre_market"
        is_open = False
    elif market_open <= now_et <= market_close:
        session_status = "regular_market_open"
        is_open = True
    else:
        session_status = "after_hours"
        is_open = False

    return {
        "calendar_available": True,
        "market": "US",
        "exchange": "NYSE",
        "is_open": bool(is_open),
        "session_status": session_status,
        "now_et": now_et.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "market_open_et": market_open.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "market_close_et": market_close.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "warning": "",
    }


def should_allow_market_order_workflow(market="US", allow_after_hours=False):
    """
    Decide whether order workflow should proceed based on market-hours status.
    """

    market = str(market or "US").upper()

    if market != "US":
        return {
            "allowed": False,
            "reason": f"Market hours check currently supports US only. Received: {market}",
            "market_hours": {},
        }

    market_hours = check_us_market_hours()

    session_status = market_hours.get("session_status")
    is_open = market_hours.get("is_open", False)

    if is_open:
        return {
            "allowed": True,
            "reason": "US regular market session is open.",
            "market_hours": market_hours,
        }

    if allow_after_hours and session_status in ["pre_market", "after_hours"]:
        return {
            "allowed": True,
            "reason": f"After-hours workflow allowed manually. Current session: {session_status}",
            "market_hours": market_hours,
        }

    return {
        "allowed": False,
        "reason": f"Order workflow blocked because market session is: {session_status}",
        "market_hours": market_hours,
    }


def get_market_hours_status():
    """
    Return compact market-hours dashboard status.
    """

    now_times = get_now_times()
    us_market = check_us_market_hours()
    workflow = should_allow_market_order_workflow(market="US", allow_after_hours=False)

    return {
        "checked_at_utc": now_times["utc_text"],
        "checked_at_us_eastern": now_times["us_eastern_text"],
        "checked_at_south_africa": now_times["south_africa_text"],
        "us_market": us_market,
        "regular_order_workflow": workflow,
    }
