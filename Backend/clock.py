"""The current time, behind a small class so the tests can fix it."""
from __future__ import annotations

from datetime import date, datetime


class Clock:
    def now(self) -> datetime:
        return datetime.now()

    def today(self) -> date:
        return self.now().date()


class FixedClock(Clock):
    """A clock that always shows the given moment (for tests and the screenshots)."""

    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        return self._moment


def day_key(day: date) -> int:
    """20261121 for 21 November 2026. Appointments keep year, month and day in separate columns."""
    return day.year * 10000 + day.month * 100 + day.day


def slot_key(moment: datetime) -> int:
    """2026112114 for 14:xx on 21 November 2026."""
    return day_key(moment.date()) * 100 + moment.hour


def next_month_start(day: date) -> date:
    return date(day.year + 1, 1, 1) if day.month == 12 else date(day.year, day.month + 1, 1)
