"""Numbers for the statistics pages. Every query lists all its grouped columns, so it also runs on MySQL 8
with the default ONLY_FULL_GROUP_BY setting."""
from __future__ import annotations

from typing import List, Optional

from ..database import Database, Row


class StatisticsRepository:
    def __init__(self, database: Database) -> None:
        self.db = database

    def dentists_by_appointments(self, limit: int = 10) -> List[Row]:
        return self.db.fetch_all(
            "SELECT d.dentist_id, d.room_number, p.first_name, p.last_name, COUNT(a.appointment_id) AS magnitude "
            "FROM appointments a JOIN dentists d ON d.dentist_id = a.d_id JOIN persons p ON p.ssn = d.dentist_ssn "
            "GROUP BY d.dentist_id, d.room_number, p.first_name, p.last_name "
            "ORDER BY magnitude DESC, d.dentist_id LIMIT %s", (limit,))

    def dentists_by_treatments(self, limit: int = 10) -> List[Row]:
        return self.db.fetch_all(
            "SELECT d.dentist_id, d.room_number, p.first_name, p.last_name, COUNT(t.treatment_id) AS magnitude "
            "FROM treatments t JOIN appointments a ON a.appointment_id = t.a_id "
            "JOIN dentists d ON d.dentist_id = a.d_id JOIN persons p ON p.ssn = d.dentist_ssn "
            "GROUP BY d.dentist_id, d.room_number, p.first_name, p.last_name "
            "ORDER BY magnitude DESC, d.dentist_id LIMIT %s", (limit,))

    def top_complaint_by_gender(self, gender: str) -> Optional[Row]:
        return self.db.fetch_one(
            "SELECT t.complaint, COUNT(*) AS magnitude FROM treatments t "
            "JOIN appointments a ON a.appointment_id = t.a_id JOIN patients pt ON pt.patient_id = a.p_id "
            "JOIN persons p ON p.ssn = pt.patient_ssn WHERE p.gender = %s "
            "GROUP BY t.complaint ORDER BY magnitude DESC, t.complaint LIMIT 1", (gender,))

    def most_expensive_treatment(self) -> Optional[Row]:
        return self.db.fetch_one(
            "SELECT t.treatment_id, t.charge, t.`action`, t.complaint, a.year, a.month, a.day, a.hour, "
            "dp.first_name AS dentist_first_name, dp.last_name AS dentist_last_name, "
            "pp.first_name AS patient_first_name, pp.last_name AS patient_last_name "
            "FROM treatments t JOIN appointments a ON a.appointment_id = t.a_id "
            "JOIN dentists d ON d.dentist_id = a.d_id JOIN persons dp ON dp.ssn = d.dentist_ssn "
            "JOIN patients pt ON pt.patient_id = a.p_id JOIN persons pp ON pp.ssn = pt.patient_ssn "
            "ORDER BY t.charge DESC, t.treatment_id LIMIT 1")

    def average_charge(self, action: str) -> Optional[float]:
        row = self.db.fetch_one("SELECT AVG(charge) AS value FROM treatments WHERE `action` = %s", (action,))
        return float(row["value"]) if row and row["value"] is not None else None

    def top_complaint_in_month(self, year: int, month: int) -> Optional[Row]:
        return self.db.fetch_one(
            "SELECT t.complaint, COUNT(*) AS magnitude FROM treatments t "
            "JOIN appointments a ON a.appointment_id = t.a_id WHERE a.year = %s AND a.month = %s "
            "GROUP BY t.complaint ORDER BY magnitude DESC, t.complaint LIMIT 1", (year, month))

    def totals(self) -> Row:
        row = self.db.fetch_one(
            "SELECT (SELECT COUNT(*) FROM patients) AS patients, (SELECT COUNT(*) FROM dentists) AS dentists, "
            "(SELECT COUNT(*) FROM appointments) AS appointments, (SELECT COUNT(*) FROM treatments) AS treatments")
        return row or {}
