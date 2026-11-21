"""Days a dentist does not work."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from ..database import Database, Row


class HolidayRepository:
    def __init__(self, database: Database) -> None:
        self.db = database

    def before(self, dentist_id: int, day: date) -> List[Row]:
        return self.db.fetch_all(
            "SELECT * FROM holiday_dates WHERE resting_id = %s AND rest_date < %s ORDER BY rest_date DESC",
            (dentist_id, day))

    def from_day(self, dentist_id: int, day: date) -> List[Row]:
        return self.db.fetch_all(
            "SELECT * FROM holiday_dates WHERE resting_id = %s AND rest_date >= %s ORDER BY rest_date",
            (dentist_id, day))

    def on_day(self, dentist_id: int, day: date) -> bool:
        return self.db.fetch_one(
            "SELECT holiday_id FROM holiday_dates WHERE resting_id = %s AND rest_date = %s",
            (dentist_id, day)) is not None

    def count_between(self, dentist_id: int, first: date, before: date) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS total FROM holiday_dates WHERE resting_id = %s AND rest_date >= %s AND rest_date < %s",
            (dentist_id, first, before))
        return int(row["total"]) if row else 0

    def find(self, dentist_id: int, holiday_id: int) -> Optional[Row]:
        return self.db.fetch_one("SELECT * FROM holiday_dates WHERE holiday_id = %s AND resting_id = %s",
                                 (holiday_id, dentist_id))

    def add(self, dentist_id: int, reason: str, day: date) -> None:
        self.db.execute("INSERT INTO holiday_dates (resting_id, reason, rest_date) VALUES (%s, %s, %s)",
                        (dentist_id, reason or None, day))

    def delete(self, dentist_id: int, holiday_id: int) -> None:
        self.db.execute("DELETE FROM holiday_dates WHERE holiday_id = %s AND resting_id = %s", (holiday_id, dentist_id))
