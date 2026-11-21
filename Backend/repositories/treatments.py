"""Treatments and the medicines given with them."""
from __future__ import annotations

from typing import List, Optional

from ..database import Database, Row


class TreatmentRepository:
    def __init__(self, database: Database) -> None:
        self.db = database

    def find(self, treatment_id: int) -> Optional[Row]:
        """The treatment together with the dentist and patient of its appointment."""
        return self.db.fetch_one(
            "SELECT t.*, a.d_id, a.p_id, a.year, a.month, a.day, a.hour FROM treatments t "
            "JOIN appointments a ON a.appointment_id = t.a_id WHERE t.treatment_id = %s", (treatment_id,))

    def for_appointment(self, appointment_id: int) -> Optional[Row]:
        return self.db.fetch_one("SELECT * FROM treatments WHERE a_id = %s", (appointment_id,))

    def create(self, appointment_id: int, dentist_id: int, action: str, complaint: str, charge: int,
               description: str) -> int:
        return self.db.execute(
            "INSERT INTO treatments (description, charge, `action`, complaint, a_id, treator_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (description or None, charge, action, complaint, appointment_id, dentist_id))

    def update(self, treatment_id: int, dentist_id: int, action: str, complaint: str, charge: int,
               description: str) -> None:
        self.db.execute(
            "UPDATE treatments SET description = %s, charge = %s, `action` = %s, complaint = %s "
            "WHERE treatment_id = %s AND treator_id = %s",
            (description or None, charge, action, complaint, treatment_id, dentist_id))

    def medicines(self, treatment_id: int) -> List[Row]:
        return self.db.fetch_all("SELECT * FROM medicines WHERE t_id = %s ORDER BY medicine_id", (treatment_id,))

    def medicine(self, treatment_id: int, medicine_id: int) -> Optional[Row]:
        return self.db.fetch_one("SELECT * FROM medicines WHERE t_id = %s AND medicine_id = %s",
                                 (treatment_id, medicine_id))

    def add_medicine(self, treatment_id: int, name: str) -> None:
        self.db.execute("INSERT INTO medicines (t_id, medicine_name) VALUES (%s, %s)", (treatment_id, name))

    def delete_medicine(self, treatment_id: int, medicine_id: int) -> None:
        self.db.execute("DELETE FROM medicines WHERE t_id = %s AND medicine_id = %s", (treatment_id, medicine_id))
