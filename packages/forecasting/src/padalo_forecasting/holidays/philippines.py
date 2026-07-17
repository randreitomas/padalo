from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


def _easter_sunday(year: int) -> date:
    """Return Gregorian Easter Sunday using the Meeus/Jones/Butcher algorithm."""

    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    weekday_offset = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * weekday_offset) // 451
    month = (h + weekday_offset - 7 * m + 114) // 31
    day = (h + weekday_offset - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def _last_monday_of_august(year: int) -> date:
    last_day = date(year, 8, 31)
    return last_day - timedelta(days=(last_day.weekday() - 0) % 7)


def philippine_holidays(start: date, end: date) -> dict[date, str]:
    """Return a compact, documented PH holiday calendar for synthetic behavior modeling."""

    holidays: dict[date, str] = {}
    for year in range(start.year, end.year + 1):
        fixed_holidays = {
            date(year, 1, 1): "New Year",
            date(year, 4, 9): "Araw ng Kagitingan",
            date(year, 5, 1): "Labor Day",
            date(year, 6, 12): "Independence Day",
            _last_monday_of_august(year): "National Heroes Day",
            date(year, 11, 30): "Bonifacio Day",
            date(year, 12, 25): "Christmas Day",
            date(year, 12, 30): "Rizal Day",
        }
        easter = _easter_sunday(year)
        fixed_holidays[easter - timedelta(days=3)] = "Maundy Thursday"
        fixed_holidays[easter - timedelta(days=2)] = "Good Friday"
        holidays.update(fixed_holidays)

    return {
        holiday_date: name
        for holiday_date, name in holidays.items()
        if start <= holiday_date <= end
    }


def philippine_holiday_frame(start: date, end: date) -> pd.DataFrame:
    rows = [
        {
            "holiday": name,
            "ds": pd.Timestamp(holiday_date),
            "lower_window": 0,
            "upper_window": 0,
        }
        for holiday_date, name in sorted(philippine_holidays(start, end).items())
    ]
    return pd.DataFrame(rows, columns=["holiday", "ds", "lower_window", "upper_window"])
