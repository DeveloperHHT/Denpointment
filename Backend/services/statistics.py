"""Numbers for the statistics page."""
from __future__ import annotations

from typing import Any, Dict

from ..catalog import ACTIONS
from ..clock import Clock
from ..repositories.statistics import StatisticsRepository


class StatisticsService:
    def __init__(self, statistics: StatisticsRepository, clock: Clock) -> None:
        self.statistics = statistics
        self.clock = clock

    def overview(self) -> Dict[str, Any]:
        today = self.clock.today()
        previous_month = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
        return {
            "totals": self.statistics.totals(),
            "busiest": self.statistics.dentists_by_appointments(5),
            "most_treatments": self.statistics.dentists_by_treatments(5),
            "top_complaint_female": self.statistics.top_complaint_by_gender("female"),
            "top_complaint_male": self.statistics.top_complaint_by_gender("male"),
            "most_expensive": self.statistics.most_expensive_treatment(),
            "average_charges": [{"action": action, "average": self.statistics.average_charge(action)}
                                for action in ACTIONS],
            "top_complaint_this_month": self.statistics.top_complaint_in_month(today.year, today.month),
            "top_complaint_last_month": self.statistics.top_complaint_in_month(*previous_month),
            "month": today,
            "previous_month": previous_month,
        }
