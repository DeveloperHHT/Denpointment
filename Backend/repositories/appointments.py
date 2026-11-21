"""Appointments. Year, month and day are separate columns, so dates are compared with a single number
(see clock.day_key and clock.slot_key)."""
from __future__ import annotations

from typing import List, Optional

from ..database import Database, Row

DAY = "(a.year * 10000 + a.month * 100 + a.day)"
SLOT = "((a.year * 10000 + a.month * 100 + a.day) * 100 + a.hour)"

_WITH_DENTIST = (
    "SELECT a.*, p.first_name, p.last_name FROM appointments a "
    "JOIN dentists d ON d.dentist_id = a.d_id JOIN persons p ON p.ssn = d.dentist_ssn ")

_WITH_PATIENT = (
    "SELECT a.*, p.first_name, p.last_name, pt.patient_id FROM appointments a "
    "JOIN patients pt ON pt.patient_id = a.p_id JOIN persons p ON p.ssn = pt.patient_ssn ")

_WITH_TREATMENT = (
    "SELECT a.*, p.first_name, p.last_name, pt.patient_id, t.treatment_id, t.charge, t.`action`, t.complaint, "
    "t.description, (SELECT COUNT(*) FROM medicines m WHERE m.t_id = t.treatment_id) AS medicine_count "
    "FROM appointments a JOIN patients pt ON pt.patient_id = a.p_id JOIN persons p ON p.ssn = pt.patient_ssn "
    "LEFT JOIN treatments t ON t.a_id = a.appointment_id ")


class AppointmentRepository:
    def __init__(self, database: Database) -> None:
        self.db = database

    def find(self, appointment_id: int) -> Optional[Row]:
        return self.db.fetch_one("SELECT a.* FROM appointments a WHERE a.appointment_id = %s", (appointment_id,))

    def create(self, dentist_id: int, patient_id: int, room: str, year: int, month: int, day: int, hour: int) -> int:
        return self.db.execute(
            "INSERT INTO appointments (d_id, p_id, room, hour, month, day, year) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (dentist_id, patient_id, room, hour, month, day, year))

    def slot_taken(self, dentist_id: int, year: int, month: int, day: int, hour: int) -> bool:
        return self.db.fetch_one(
            "SELECT appointment_id FROM appointments WHERE d_id = %s AND year = %s AND month = %s AND day = %s "
            "AND hour = %s", (dentist_id, year, month, day, hour)) is not None

    def dentist_has_patient(self, dentist_id: int, patient_id: int) -> bool:
        return self.db.fetch_one("SELECT appointment_id FROM appointments WHERE d_id = %s AND p_id = %s LIMIT 1",
                                 (dentist_id, patient_id)) is not None

    # -- patient side -----------------------------------------------------------------------

    def upcoming_for_patient(self, patient_id: int, now_slot: int) -> List[Row]:
        return self.db.fetch_all(
            _WITH_DENTIST + f"WHERE a.p_id = %s AND {SLOT} > %s ORDER BY {SLOT}", (patient_id, now_slot))

    def past_for_patient(self, patient_id: int, now_slot: int) -> List[Row]:
        return self.db.fetch_all(
            "SELECT a.*, p.first_name, p.last_name, t.treatment_id, t.charge, t.`action`, t.complaint, "
            "(SELECT COUNT(*) FROM medicines m WHERE m.t_id = t.treatment_id) AS medicine_count "
            "FROM appointments a JOIN dentists d ON d.dentist_id = a.d_id JOIN persons p ON p.ssn = d.dentist_ssn "
            "LEFT JOIN treatments t ON t.a_id = a.appointment_id "
            f"WHERE a.p_id = %s AND {SLOT} <= %s ORDER BY {SLOT} DESC", (patient_id, now_slot))

    # -- dentist side -----------------------------------------------------------------------

    def upcoming_for_dentist(self, dentist_id: int, today_key: int) -> List[Row]:
        return self.db.fetch_all(
            _WITH_PATIENT + f"WHERE a.d_id = %s AND {DAY} > %s ORDER BY {SLOT}", (dentist_id, today_key))

    def on_day_for_dentist(self, dentist_id: int, day_key_value: int) -> List[Row]:
        return self.db.fetch_all(
            _WITH_TREATMENT + f"WHERE a.d_id = %s AND {DAY} = %s ORDER BY a.hour", (dentist_id, day_key_value))

    def past_for_dentist(self, dentist_id: int, today_key: int) -> List[Row]:
        return self.db.fetch_all(
            _WITH_TREATMENT + f"WHERE a.d_id = %s AND {DAY} < %s ORDER BY {SLOT} DESC", (dentist_id, today_key))
