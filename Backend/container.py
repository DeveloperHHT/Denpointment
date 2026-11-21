"""Builds the repositories and services of a request from its database connection and the clock."""
from __future__ import annotations

from functools import cached_property

from flask import current_app, g

from .clock import Clock
from .database import Database, get_database
from .repositories.appointments import AppointmentRepository
from .repositories.holidays import HolidayRepository
from .repositories.persons import PersonRepository
from .repositories.statistics import StatisticsRepository
from .repositories.treatments import TreatmentRepository
from .services.auth import AuthService, PasswordHasher
from .services.booking import BookingService
from .services.holidays import HolidayService
from .services.profile import PatientDirectory, ProfileService
from .services.statistics import StatisticsService
from .services.treatments import TreatmentService


class Services:
    def __init__(self, database: Database, clock: Clock, hasher: PasswordHasher) -> None:
        self._database = database
        self._clock = clock
        self._hasher = hasher

    @cached_property
    def persons(self) -> PersonRepository:
        return PersonRepository(self._database)

    @cached_property
    def appointments(self) -> AppointmentRepository:
        return AppointmentRepository(self._database)

    @cached_property
    def auth(self) -> AuthService:
        return AuthService(self.persons, self._hasher)

    @cached_property
    def profile(self) -> ProfileService:
        return ProfileService(self.persons)

    @cached_property
    def patients(self) -> PatientDirectory:
        return PatientDirectory(self.persons, self.appointments)

    @cached_property
    def booking(self) -> BookingService:
        return BookingService(self.persons, self.appointments, HolidayRepository(self._database), self._clock)

    @cached_property
    def holidays(self) -> HolidayService:
        return HolidayService(self.persons, HolidayRepository(self._database), self._clock)

    @cached_property
    def treatments(self) -> TreatmentService:
        return TreatmentService(self.persons, self.appointments, TreatmentRepository(self._database), self._clock)

    @cached_property
    def statistics(self) -> StatisticsService:
        return StatisticsService(StatisticsRepository(self._database), self._clock)


def get_services() -> Services:
    if "services" not in g:
        g.services = Services(get_database(), current_app.config["CLOCK"], current_app.config["HASHER"])
    return g.services
