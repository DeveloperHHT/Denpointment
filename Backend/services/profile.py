"""A person's own data: addresses, phone numbers and chronic diseases."""
from __future__ import annotations

from typing import Any, Dict

from ..exceptions import RuleViolation
from ..repositories.persons import PersonRepository


class ProfileService:
    def __init__(self, persons: PersonRepository) -> None:
        self.persons = persons

    def overview(self, ssn: str) -> Dict[str, Any]:
        return {
            "person": self.persons.find_by_ssn(ssn),
            "addresses": self.persons.addresses(ssn),
            "phones": self.persons.phones(ssn),
            "chronic_diseases": self.persons.chronic_diseases(ssn),
        }

    def activate_patient_if_ready(self, ssn: str) -> bool:
        """A person becomes a patient once there is at least one address and one phone number.
        Returns True when this call made them a patient."""
        if self.persons.patient_id(ssn) is not None:
            return False
        if self.persons.addresses(ssn) and self.persons.phones(ssn):
            self.persons.create_patient(ssn)
            return True
        return False

    # -- addresses --------------------------------------------------------------------------

    def add_address(self, ssn: str, city: str, street: str, zip_code: str) -> None:
        if self.persons.address_exists(ssn, city, street, zip_code):
            raise RuleViolation("This address is already in your profile.")
        self.persons.add_address(ssn, city, street, zip_code)

    def update_address(self, ssn: str, address_id: int, city: str, street: str, zip_code: str) -> None:
        self.get_address(ssn, address_id)
        if self.persons.address_exists(ssn, city, street, zip_code):
            raise RuleViolation("This address is already in your profile.")
        self.persons.update_address(ssn, address_id, city, street, zip_code)

    def get_address(self, ssn: str, address_id: int):
        address = self.persons.address(ssn, address_id)
        if address is None:
            raise RuleViolation("There is no such address in your profile.")
        return address

    def delete_address(self, ssn: str, address_id: int) -> None:
        self.get_address(ssn, address_id)
        if len(self.persons.addresses(ssn)) <= 1:
            raise RuleViolation("You need at least one address. You can edit the existing one instead.")
        self.persons.delete_address(ssn, address_id)

    # -- phone numbers ----------------------------------------------------------------------

    def add_phone(self, ssn: str, number: str) -> None:
        if self.persons.phone_exists(number):
            raise RuleViolation("This phone number has already been registered.")
        self.persons.add_phone(ssn, number)

    def get_phone(self, ssn: str, number: str):
        phone = self.persons.phone(ssn, number)
        if phone is None:
            raise RuleViolation("There is no such phone number in your profile.")
        return phone

    def update_phone(self, ssn: str, old_number: str, new_number: str) -> None:
        self.get_phone(ssn, old_number)
        if new_number != old_number and self.persons.phone_exists(new_number):
            raise RuleViolation("This phone number has already been registered.")
        self.persons.update_phone(ssn, old_number, new_number)

    def delete_phone(self, ssn: str, number: str) -> None:
        self.get_phone(ssn, number)
        if len(self.persons.phones(ssn)) <= 1:
            raise RuleViolation("You need at least one phone number. You can edit the existing one instead.")
        self.persons.delete_phone(ssn, number)

    # -- chronic diseases -------------------------------------------------------------------

    def add_chronic_disease(self, ssn: str, name: str) -> None:
        if self.persons.chronic_disease_exists(ssn, name):
            raise RuleViolation("This chronic disease is already in your profile.")
        self.persons.add_chronic_disease(ssn, name)

    def delete_chronic_disease(self, ssn: str, name: str) -> None:
        if not self.persons.chronic_disease_exists(ssn, name):
            raise RuleViolation("There is no such chronic disease in your profile.")
        self.persons.delete_chronic_disease(ssn, name)


class PatientDirectory:
    """What a dentist may see about a patient: only patients who have booked with them."""

    def __init__(self, persons: PersonRepository, appointments) -> None:
        self.persons = persons
        self.appointments = appointments

    def overview(self, dentist_ssn: str, patient_id: int) -> Dict[str, Any]:
        dentist = self.persons.dentist(dentist_ssn)
        patient = self.persons.patient_with_person(patient_id)
        if dentist is None:
            raise RuleViolation("You are not authorized!")
        if patient is None or not self.appointments.dentist_has_patient(dentist["dentist_id"], patient_id):
            raise RuleViolation("There is no such patient among your appointments.")
        ssn = patient["ssn"]
        return {
            "patient": patient,
            "addresses": self.persons.addresses(ssn),
            "phones": self.persons.phones(ssn),
            "chronic_diseases": self.persons.chronic_diseases(ssn),
        }
