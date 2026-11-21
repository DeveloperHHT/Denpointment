"""People, their contact data and their roles (patient or dentist)."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from ..database import Database, Row


class PersonRepository:
    def __init__(self, database: Database) -> None:
        self.db = database

    # -- person -----------------------------------------------------------------------------

    def find_by_email(self, email: str) -> Optional[Row]:
        return self.db.fetch_one("SELECT * FROM persons WHERE email = %s", (email,))

    def find_by_ssn(self, ssn: str) -> Optional[Row]:
        return self.db.fetch_one("SELECT * FROM persons WHERE ssn = %s", (ssn,))

    def create(self, ssn: str, email: str, password_hash: str, first_name: str, last_name: str,
               gender: str, birth_date: date) -> None:
        self.db.execute(
            "INSERT INTO persons (ssn, email, password, first_name, last_name, gender, birth_date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (ssn, email, password_hash, first_name, last_name, gender, birth_date))

    def update_password(self, ssn: str, password_hash: str) -> None:
        self.db.execute("UPDATE persons SET password = %s WHERE ssn = %s", (password_hash, ssn))

    def update_email(self, ssn: str, email: str) -> None:
        self.db.execute("UPDATE persons SET email = %s WHERE ssn = %s", (email, ssn))

    # -- roles ------------------------------------------------------------------------------

    def patient_id(self, ssn: str) -> Optional[int]:
        row = self.db.fetch_one("SELECT patient_id FROM patients WHERE patient_ssn = %s", (ssn,))
        return row["patient_id"] if row else None

    def dentist(self, ssn: str) -> Optional[Row]:
        return self.db.fetch_one("SELECT * FROM dentists WHERE dentist_ssn = %s", (ssn,))

    def create_patient(self, ssn: str) -> int:
        return self.db.execute("INSERT INTO patients (patient_ssn) VALUES (%s)", (ssn,))

    def patient_with_person(self, patient_id: int) -> Optional[Row]:
        return self.db.fetch_one(
            "SELECT patients.patient_id, persons.* FROM patients "
            "JOIN persons ON persons.ssn = patients.patient_ssn WHERE patients.patient_id = %s", (patient_id,))

    def dentists(self) -> List[Row]:
        return self.db.fetch_all(
            "SELECT dentists.dentist_id, dentists.room_number, persons.first_name, persons.last_name "
            "FROM dentists JOIN persons ON persons.ssn = dentists.dentist_ssn "
            "ORDER BY persons.first_name, persons.last_name")

    def dentist_by_id(self, dentist_id: int) -> Optional[Row]:
        return self.db.fetch_one(
            "SELECT dentists.dentist_id, dentists.room_number, persons.first_name, persons.last_name "
            "FROM dentists JOIN persons ON persons.ssn = dentists.dentist_ssn WHERE dentists.dentist_id = %s",
            (dentist_id,))

    # -- addresses --------------------------------------------------------------------------

    def addresses(self, ssn: str) -> List[Row]:
        return self.db.fetch_all("SELECT * FROM addresses WHERE p_ssn = %s ORDER BY address_id", (ssn,))

    def address(self, ssn: str, address_id: int) -> Optional[Row]:
        return self.db.fetch_one("SELECT * FROM addresses WHERE p_ssn = %s AND address_id = %s", (ssn, address_id))

    def address_exists(self, ssn: str, city: str, street: str, zip_code: str) -> bool:
        return self.db.fetch_one(
            "SELECT address_id FROM addresses WHERE p_ssn = %s AND city = %s AND street = %s AND zip_code = %s",
            (ssn, city, street, zip_code)) is not None

    def add_address(self, ssn: str, city: str, street: str, zip_code: str) -> None:
        self.db.execute("INSERT INTO addresses (p_ssn, city, street, zip_code) VALUES (%s, %s, %s, %s)",
                        (ssn, city, street, zip_code))

    def update_address(self, ssn: str, address_id: int, city: str, street: str, zip_code: str) -> None:
        self.db.execute("UPDATE addresses SET city = %s, street = %s, zip_code = %s WHERE p_ssn = %s AND address_id = %s",
                        (city, street, zip_code, ssn, address_id))

    def delete_address(self, ssn: str, address_id: int) -> None:
        self.db.execute("DELETE FROM addresses WHERE p_ssn = %s AND address_id = %s", (ssn, address_id))

    # -- phone numbers ----------------------------------------------------------------------

    def phones(self, ssn: str) -> List[Row]:
        return self.db.fetch_all(
            "SELECT * FROM person_contact_numbers WHERE contact_ssn = %s ORDER BY contact_number", (ssn,))

    def phone(self, ssn: str, number: str) -> Optional[Row]:
        return self.db.fetch_one(
            "SELECT * FROM person_contact_numbers WHERE contact_ssn = %s AND contact_number = %s", (ssn, number))

    def phone_exists(self, number: str) -> bool:
        return self.db.fetch_one(
            "SELECT contact_number FROM person_contact_numbers WHERE contact_number = %s", (number,)) is not None

    def add_phone(self, ssn: str, number: str) -> None:
        self.db.execute("INSERT INTO person_contact_numbers (contact_number, contact_ssn) VALUES (%s, %s)",
                        (number, ssn))

    def update_phone(self, ssn: str, old_number: str, new_number: str) -> None:
        self.db.execute(
            "UPDATE person_contact_numbers SET contact_number = %s WHERE contact_ssn = %s AND contact_number = %s",
            (new_number, ssn, old_number))

    def delete_phone(self, ssn: str, number: str) -> None:
        self.db.execute("DELETE FROM person_contact_numbers WHERE contact_ssn = %s AND contact_number = %s",
                        (ssn, number))

    # -- chronic diseases -------------------------------------------------------------------

    def chronic_diseases(self, ssn: str) -> List[Row]:
        return self.db.fetch_all(
            "SELECT * FROM chronic_diseases WHERE chronic_ssn = %s ORDER BY chronic_disease", (ssn,))

    def chronic_disease_exists(self, ssn: str, name: str) -> bool:
        return self.db.fetch_one(
            "SELECT chronic_disease FROM chronic_diseases WHERE chronic_ssn = %s AND chronic_disease = %s",
            (ssn, name)) is not None

    def add_chronic_disease(self, ssn: str, name: str) -> None:
        self.db.execute("INSERT INTO chronic_diseases (chronic_disease, chronic_ssn) VALUES (%s, %s)", (name, ssn))

    def delete_chronic_disease(self, ssn: str, name: str) -> None:
        self.db.execute("DELETE FROM chronic_diseases WHERE chronic_ssn = %s AND chronic_disease = %s", (ssn, name))
