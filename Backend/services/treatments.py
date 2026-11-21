"""Dentists recording what they did during today's appointments."""
from __future__ import annotations

from typing import Any, Dict, List

from ..clock import Clock, day_key
from ..database import Row
from ..exceptions import RuleViolation
from ..repositories.appointments import AppointmentRepository
from ..repositories.persons import PersonRepository
from ..repositories.treatments import TreatmentRepository


class TreatmentService:
    def __init__(self, persons: PersonRepository, appointments: AppointmentRepository,
                 treatments: TreatmentRepository, clock: Clock) -> None:
        self.persons = persons
        self.appointments = appointments
        self.treatments = treatments
        self.clock = clock

    def _dentist_id(self, ssn: str) -> int:
        dentist = self.persons.dentist(ssn)
        if dentist is None:
            raise RuleViolation("You are not authorized!")
        return dentist["dentist_id"]

    # -- lists ------------------------------------------------------------------------------

    def upcoming(self, ssn: str) -> List[Row]:
        return self.appointments.upcoming_for_dentist(self._dentist_id(ssn), day_key(self.clock.today()))

    def today(self, ssn: str) -> List[Row]:
        return self.appointments.on_day_for_dentist(self._dentist_id(ssn), day_key(self.clock.today()))

    def history(self, ssn: str) -> List[Row]:
        return self.appointments.past_for_dentist(self._dentist_id(ssn), day_key(self.clock.today()))

    # -- the appointment a treatment belongs to ---------------------------------------------

    def _todays_appointment(self, dentist_id: int, appointment_id: int) -> Row:
        appointment = self.appointments.find(appointment_id)
        if appointment is None or appointment["d_id"] != dentist_id:
            raise RuleViolation("There is no such appointment in your schedule.")
        today = self.clock.today()
        if (appointment["year"], appointment["month"], appointment["day"]) != (today.year, today.month, today.day):
            raise RuleViolation("You can only record a treatment for today's appointments.", "warning")
        return appointment

    def appointment_with_patient(self, ssn: str, appointment_id: int) -> Dict[str, Any]:
        dentist_id = self._dentist_id(ssn)
        appointment = self._todays_appointment(dentist_id, appointment_id)
        return {"appointment": appointment, "patient": self.persons.patient_with_person(appointment["p_id"]),
                "treatment": self.treatments.for_appointment(appointment_id)}

    def add(self, ssn: str, appointment_id: int, action: str, complaint: str, charge: int, description: str) -> int:
        dentist_id = self._dentist_id(ssn)
        self._todays_appointment(dentist_id, appointment_id)
        if self.treatments.for_appointment(appointment_id) is not None:
            raise RuleViolation("This appointment already has a treatment. You can edit it instead.", "warning")
        return self.treatments.create(appointment_id, dentist_id, action, complaint, charge, description)

    # -- an existing treatment --------------------------------------------------------------

    def get(self, ssn: str, treatment_id: int) -> Dict[str, Any]:
        """A treatment of this dentist with its medicines and patient."""
        dentist_id = self._dentist_id(ssn)
        treatment = self.treatments.find(treatment_id)
        if treatment is None or treatment["treator_id"] != dentist_id:
            raise RuleViolation("There is no such treatment in your records.")
        return {"treatment": treatment, "patient": self.persons.patient_with_person(treatment["p_id"]),
                "medicines": self.treatments.medicines(treatment_id)}

    def edit(self, ssn: str, treatment_id: int, action: str, complaint: str, charge: int, description: str) -> None:
        treatment = self.get(ssn, treatment_id)["treatment"]
        self._todays_appointment(treatment["treator_id"], treatment["a_id"])
        self.treatments.update(treatment_id, treatment["treator_id"], action, complaint, charge, description)

    def add_medicine(self, ssn: str, treatment_id: int, name: str) -> None:
        treatment = self.get(ssn, treatment_id)["treatment"]
        self._todays_appointment(treatment["treator_id"], treatment["a_id"])
        if any(m["medicine_name"].lower() == name.lower() for m in self.treatments.medicines(treatment_id)):
            raise RuleViolation("This medicine is already on the list.", "warning")
        self.treatments.add_medicine(treatment_id, name)

    def delete_medicine(self, ssn: str, treatment_id: int, medicine_id: int) -> None:
        treatment = self.get(ssn, treatment_id)["treatment"]
        self._todays_appointment(treatment["treator_id"], treatment["a_id"])
        if self.treatments.medicine(treatment_id, medicine_id) is None:
            raise RuleViolation("There is no such medicine on the list.")
        self.treatments.delete_medicine(treatment_id, medicine_id)

    # -- patients looking at their own ------------------------------------------------------

    def for_patient(self, ssn: str, treatment_id: int) -> Dict[str, Any]:
        patient_id = self.persons.patient_id(ssn)
        treatment = self.treatments.find(treatment_id)
        if patient_id is None or treatment is None or treatment["p_id"] != patient_id:
            raise RuleViolation("There is no such treatment in your records.")
        dentist = self.persons.dentist_by_id(treatment["d_id"])
        return {"treatment": treatment, "dentist": dentist, "medicines": self.treatments.medicines(treatment_id)}
