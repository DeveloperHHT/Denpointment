"""Creates the SQLite demo database with made-up people, appointments and treatments.

Every date is relative to `today`, so the demo always has past, today's and upcoming appointments.

    python Scripts/seed_demo.py            (re)creates Data/demo.db

All demo accounts use the password "demo1234":
    patient@denpointment.example    a patient with an upcoming appointment and a history
    patient2@denpointment.example   a patient who can book an appointment right now
    fresh@denpointment.example      a new account: add an address and a phone number to become a patient
    dentist@denpointment.example    a dentist with appointments today, upcoming ones and holidays
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Backend.app import ensure_sqlite_schema  # noqa: E402
from Backend.clock import next_month_start  # noqa: E402
from Backend.config import Settings  # noqa: E402
from Backend.database import Database  # noqa: E402
from Backend.services.auth import PasswordHasher  # noqa: E402

PASSWORD = "demo1234"

DENTISTS = [  # ssn, email, first, last, gender, room
    ("90000000001", "dentist@denpointment.example", "Elif", "Aydin", "female", "101"),
    ("90000000002", "k.bright@denpointment.example", "Kerem", "Bright", "male", "102"),
    ("90000000003", "n.stone@denpointment.example", "Nora", "Stone", "female", "201"),
    ("90000000004", "m.vale@denpointment.example", "Mert", "Vale", "male", "202"),
]

PATIENTS = [  # ssn, email, first, last, gender, birth, city, street, zip, phone, chronic
    ("80000000001", "patient@denpointment.example", "Deniz", "Kaya", "male", date(1991, 4, 12), "Ankara", "Elm Street", "06100", "5550000001", "asthma"),
    ("80000000002", "patient2@denpointment.example", "Selin", "Arda", "female", date(1988, 9, 3), "Izmir", "Harbour Road", "35000", "5550000002", None),
    ("80000000003", "j.moor@denpointment.example", "Jon", "Moor", "male", date(1979, 1, 25), "Bursa", "Mill Lane", "16000", "5550000003", "diabetes"),
    ("80000000004", "a.rey@denpointment.example", "Ada", "Rey", "female", date(2000, 6, 30), "Konya", "Park Avenue", "42000", "5550000004", None),
    ("80000000005", "o.finn@denpointment.example", "Oscar", "Finn", "male", date(1995, 11, 8), "Adana", "Lake View", "01000", "5550000005", None),
]

FRESH = ("80000000009", "fresh@denpointment.example", "Lale", "Demir", "female", date(1999, 2, 14))

TREATMENTS = [  # action, complaint, charge, note
    ("root canal treatment", "toothache", 340, "control after this treatment requested"),
    ("dental filling", "general inspection", 85, None),
    ("teeth whitening", "annual inspection", 210, None),
    ("tooth decay treatment", "toothache", 120, None),
    ("dental implant", "inspection after treatmen", 900, "x-ray taken"),
    ("dental filling", "annual inspection", 95, None),
    ("tooth decay treatment", "general inspection", 130, None),
    ("root canal treatment", "toothache", 360, None),
]

MEDICINES = ["Amoxicillin 500 mg", "Ibuprofen 400 mg", "Chlorhexidine rinse"]


class DemoBuilder:
    def __init__(self, db: Database, password_hash: str, today: date) -> None:
        self.db = db
        self.password_hash = password_hash
        self.today = today

    def person(self, ssn: str, email: str, first: str, last: str, gender: str, birth: date) -> None:
        self.db.execute(
            "INSERT INTO persons (ssn, email, password, first_name, last_name, gender, birth_date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)", (ssn, email, self.password_hash, first, last, gender, birth))

    def appointment(self, dentist_id: int, patient_id: int, room: str, day: date, hour: int) -> int:
        return self.db.execute(
            "INSERT INTO appointments (d_id, p_id, room, hour, month, day, year) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (dentist_id, patient_id, room, hour, day.month, day.day, day.year))

    def treatment(self, appointment_id: int, dentist_id: int, index: int, medicines: int = 0) -> None:
        action, complaint, charge, note = TREATMENTS[index % len(TREATMENTS)]
        treatment_id = self.db.execute(
            "INSERT INTO treatments (description, charge, `action`, complaint, a_id, treator_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)", (note, charge, action, complaint, appointment_id, dentist_id))
        for name in MEDICINES[:medicines]:
            self.db.execute("INSERT INTO medicines (t_id, medicine_name) VALUES (%s, %s)", (treatment_id, name))

    def build(self) -> None:
        dentist_ids: List[int] = []
        for ssn, email, first, last, gender, room in DENTISTS:
            self.person(ssn, email, first, last, gender, date(1980, 5, 17))
            dentist_ids.append(self.db.execute("INSERT INTO dentists (dentist_ssn, room_number) VALUES (%s, %s)", (ssn, room)))

        patient_ids: List[int] = []
        for ssn, email, first, last, gender, birth, city, street, zip_code, phone, chronic in PATIENTS:
            self.person(ssn, email, first, last, gender, birth)
            self.db.execute("INSERT INTO addresses (p_ssn, city, street, zip_code) VALUES (%s, %s, %s, %s)", (ssn, city, street, zip_code))
            self.db.execute("INSERT INTO person_contact_numbers (contact_number, contact_ssn) VALUES (%s, %s)", (phone, ssn))
            if chronic:
                self.db.execute("INSERT INTO chronic_diseases (chronic_disease, chronic_ssn) VALUES (%s, %s)", (chronic, ssn))
            patient_ids.append(self.db.execute("INSERT INTO patients (patient_ssn) VALUES (%s)", (ssn,)))

        self.person(*FRESH)

        rooms = {i: d[5] for i, d in zip(dentist_ids, DENTISTS)}
        main_dentist = dentist_ids[0]
        today = self.today

        # History: every dentist has seen several patients on different days.
        hours = (8, 9, 10, 11, 12, 15, 16)
        for n in range(18):
            dentist_id = dentist_ids[n % len(dentist_ids)]
            patient_id = patient_ids[(n * 2 + n // 3) % len(patient_ids)]
            day = today - timedelta(days=3 + n * 2)
            appointment_id = self.appointment(dentist_id, patient_id, rooms[dentist_id], day, hours[n % len(hours)])
            self.treatment(appointment_id, dentist_id, n, medicines=(n % 3))
        # Deniz (the demo patient) has seen the demo dentist a few times.
        for n, offset in enumerate((6, 21, 40)):
            appointment_id = self.appointment(main_dentist, patient_ids[0], rooms[main_dentist], today - timedelta(days=offset), (9, 11, 15)[n])
            self.treatment(appointment_id, main_dentist, n + 3, medicines=2 - n % 2)

        # Today: three appointments of the demo dentist, the first one already has its treatment.
        for n, (patient_index, hour) in enumerate(((1, 9), (2, 11), (3, 15))):
            appointment_id = self.appointment(main_dentist, patient_ids[patient_index], rooms[main_dentist], today, hour)
            if n == 0:
                self.treatment(appointment_id, main_dentist, 1, medicines=1)

        # Upcoming.
        self.appointment(main_dentist, patient_ids[0], rooms[main_dentist], today + timedelta(days=3), 10)
        self.appointment(main_dentist, patient_ids[4], rooms[main_dentist], today + timedelta(days=4), 16)
        self.appointment(dentist_ids[1], patient_ids[2], rooms[dentist_ids[1]], today + timedelta(days=2), 12)

        # Holidays of the demo dentist: one in the past, two next month.
        first_of_next = next_month_start(today.replace(day=1))
        for reason, day in (("Conference", today - timedelta(days=30)), ("Family visit", first_of_next + timedelta(days=9)),
                            ("Weekend trip", first_of_next + timedelta(days=15))):
            self.db.execute("INSERT INTO holiday_dates (resting_id, reason, rest_date) VALUES (%s, %s, %s)", (main_dentist, reason, day))


def prepare_demo_database(settings: Settings, today: Optional[date] = None, rounds: int = 535000) -> None:
    """Replaces the SQLite file of `settings` with a fresh demo database."""
    path = settings.sqlite_path
    if path.exists():
        path.unlink()
    ensure_sqlite_schema(settings)
    db = Database(settings)
    try:
        DemoBuilder(db, PasswordHasher(rounds).hash(PASSWORD), today or date.today()).build()
    finally:
        db.close()


if __name__ == "__main__":
    demo_settings = Settings.from_environment()
    from dataclasses import replace

    demo_settings = replace(demo_settings, backend="sqlite")
    prepare_demo_database(demo_settings)
    print(f"Demo database written to {demo_settings.sqlite_path}")
    print(f"Log in with patient@denpointment.example or dentist@denpointment.example, password {PASSWORD}")
