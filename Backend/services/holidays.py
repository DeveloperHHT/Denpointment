"""Dentists planning their days off."""
from __future__ import annotations

from datetime import date
from typing import Dict, List

from ..clock import Clock, next_month_start
from ..database import Row
from ..exceptions import RuleViolation
from ..repositories.holidays import HolidayRepository
from ..repositories.persons import PersonRepository

MAX_DAYS_PER_MONTH = 3


class HolidayService:
    def __init__(self, persons: PersonRepository, holidays: HolidayRepository, clock: Clock) -> None:
        self.persons = persons
        self.holidays = holidays
        self.clock = clock

    def _dentist_id(self, ssn: str) -> int:
        dentist = self.persons.dentist(ssn)
        if dentist is None:
            raise RuleViolation("You are not authorized!")
        return dentist["dentist_id"]

    def overview(self, ssn: str) -> Dict[str, List[Row]]:
        dentist_id = self._dentist_id(ssn)
        today = self.clock.today()
        return {"upcoming": self.holidays.from_day(dentist_id, today), "past": self.holidays.before(dentist_id, today)}

    def add(self, ssn: str, day: date, reason: str) -> None:
        dentist_id = self._dentist_id(ssn)
        this_month = self.clock.today().replace(day=1)
        first = next_month_start(this_month)
        if not first <= day < next_month_start(first):
            raise RuleViolation("A holiday must be in the next month.")
        if self.holidays.on_day(dentist_id, day):
            raise RuleViolation("This holiday has already been registered.")
        if self.holidays.count_between(dentist_id, first, next_month_start(first)) >= MAX_DAYS_PER_MONTH:
            raise RuleViolation(f"You can rest at most {MAX_DAYS_PER_MONTH} days in a month.", "warning")
        self.holidays.add(dentist_id, reason, day)

    def delete(self, ssn: str, holiday_id: int) -> None:
        dentist_id = self._dentist_id(ssn)
        holiday = self.holidays.find(dentist_id, holiday_id)
        if holiday is None:
            raise RuleViolation("There is no such holiday in your profile.")
        today = self.clock.today()
        if (holiday["rest_date"].year, holiday["rest_date"].month) <= (today.year, today.month):
            raise RuleViolation("You cannot delete a holiday that is in this month or has passed.")
        self.holidays.delete(dentist_id, holiday_id)
