"""Registration, login and changing credentials."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict

from passlib.hash import sha256_crypt

from ..database import Row
from ..exceptions import RuleViolation
from ..repositories.persons import PersonRepository


class PasswordHasher:
    """sha256_crypt, the scheme the existing database already uses."""

    def __init__(self, rounds: int = 535000) -> None:
        self._scheme = sha256_crypt.using(rounds=rounds)

    def hash(self, password: str) -> str:
        return self._scheme.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        try:
            return self._scheme.verify(password, hashed)
        except ValueError:  # a value that is not a sha256_crypt hash (some sample rows)
            return False


class AuthService:
    def __init__(self, persons: PersonRepository, hasher: PasswordHasher) -> None:
        self.persons = persons
        self.hasher = hasher

    def register(self, ssn: str, email: str, password: str, first_name: str, last_name: str, gender: str,
                 birth_date: date) -> None:
        if self.persons.find_by_ssn(ssn):
            raise RuleViolation("This SSN has already been registered.")
        if self.persons.find_by_email(email):
            raise RuleViolation("This email has already been registered.")
        self.persons.create(ssn, email, self.hasher.hash(password), first_name, last_name, gender, birth_date)

    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Returns what goes into the session. The same message for both failures, so emails cannot be probed."""
        person = self.persons.find_by_email(email)
        if person is None or not self.hasher.verify(password, person["password"]):
            raise RuleViolation("The email or the password is wrong.")
        return self.session_data(person)

    def session_data(self, person: Row) -> Dict[str, Any]:
        ssn = person["ssn"]
        return {
            "ssn": ssn,
            "email": person["email"],
            "full_name": f"{person['first_name']} {person['last_name']}",
            "is_patient": self.persons.patient_id(ssn) is not None,
            "is_dentist": self.persons.dentist(ssn) is not None,
        }

    def change_password(self, ssn: str, old_password: str, new_password: str) -> None:
        person = self._person(ssn)
        if not self.hasher.verify(old_password, person["password"]):
            raise RuleViolation("Your current password is wrong.")
        if old_password == new_password:
            raise RuleViolation("Your old password and new password cannot be the same.")
        self.persons.update_password(ssn, self.hasher.hash(new_password))

    def change_email(self, ssn: str, new_email: str, password: str) -> None:
        person = self._person(ssn)
        if not self.hasher.verify(password, person["password"]):
            raise RuleViolation("Your password is wrong.")
        if person["email"] == new_email:
            raise RuleViolation("Your old email and new email cannot be the same.")
        if self.persons.find_by_email(new_email):
            raise RuleViolation("This email has already been registered.")
        self.persons.update_email(ssn, new_email)

    def _person(self, ssn: str) -> Row:
        person = self.persons.find_by_ssn(ssn)
        if person is None:
            raise RuleViolation("Your account could not be found.")
        return person
