"""Patients booking appointments and looking at their own."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Tuple

from ..clock import Clock, slot_key
from ..exceptions import RuleViolation
from ..repositories.appointments import AppointmentRepository
from ..repositories.holidays import HolidayRepository
from ..repositories.persons import PersonRepository

# Working hours of the clinic: the lunch break is 13:00-15:00.
HOURS: Tuple[int, ...] = (8, 9, 10, 11, 12, 15, 16)


class BookingService:
    def __init__(self, persons: PersonRepository, appointments: AppointmentRepository,
                 holidays: HolidayRepository, clock: Clock) -> None:
        self.persons = persons
        self.appointments = appointments
        self.holidays = holidays
        self.clock = clock

    def _patient_id(self, ssn: str) -> int:
        patient_id = self.persons.patient_id(ssn)
        if patient_id is None:
            raise RuleViolation("You need to add an address and a phone number before you can book.")
        return patient_id

    def my_appointments(self, ssn: str) -> Dict[str, List[Any]]:
        patient_id = self._patient_id(ssn)
        now = slot_key(self.clock.now())
        return {"upcoming": self.appointments.upcoming_for_patient(patient_id, now),
                "past": self.appointments.past_for_patient(patient_id, now)}

    def has_upcoming(self, ssn: str) -> bool:
        patient_id = self._patient_id(ssn)
        return bool(self.appointments.upcoming_for_patient(patient_id, slot_key(self.clock.now())))

    def book(self, ssn: str, dentist_id: int, day: date, hour: int) -> None:
        patient_id = self._patient_id(ssn)
        now = self.clock.now()

        if self.appointments.upcoming_for_patient(patient_id, slot_key(now)):
            raise RuleViolation("You already have an upcoming appointment. You can book another one after it.")
        if hour not in HOURS:
            raise RuleViolation("Please choose one of the working hours.")
        if (day.year, day.month) != (now.year, now.month) or day < now.date():
            raise RuleViolation("You can only get an appointment for the rest of this month.")
        if day == now.date() and hour <= now.hour:
            raise RuleViolation("You cannot get an appointment for a time that has already passed.")

        dentist = self.persons.dentist_by_id(dentist_id)
        if dentist is None:
            raise RuleViolation("This dentist does not exist.")
        name = f"{dentist['first_name']} {dentist['last_name']}"

        if self.holidays.on_day(dentist_id, day):
            raise RuleViolation(f"{name} is on holiday on that day, please choose another date.", "warning")
        if self.appointments.slot_taken(dentist_id, day.year, day.month, day.day, hour):
            raise RuleViolation(f"{name} already has an appointment on {day.day}/{day.month}/{day.year} at {hour}:00.")

        self.appointments.create(dentist_id, patient_id, dentist["room_number"], day.year, day.month, day.day, hour)
