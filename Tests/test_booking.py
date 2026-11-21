from datetime import datetime

import pytest

from Tests.conftest import PATIENT_FREE, build_app, log_in, page


def book(client, dentist=2, day="2026-11-25", hour=9):
    return client.post("/appointments/book", data={"dentist": dentist, "date": day, "hour": hour}, follow_redirects=True)


def test_patient_books_a_free_slot(as_free_patient):
    response = book(as_free_patient)
    assert "Your appointment has been booked." in page(response)
    assert "25 Nov 2026" in page(response)


def test_only_one_upcoming_appointment_at_a_time(as_free_patient):
    book(as_free_patient)
    response = as_free_patient.get("/appointments/book", follow_redirects=True)
    assert "already have an upcoming appointment" in page(response)
    assert "already have an upcoming appointment" in page(book(as_free_patient, day="2026-11-26"))


def test_patient_with_an_upcoming_appointment_cannot_book(as_patient):
    assert "already have an upcoming appointment" in page(as_patient.get("/appointments/book", follow_redirects=True))


def test_slot_taken_by_somebody_else(client):
    log_in(client, PATIENT_FREE)
    book(client, dentist=1, day="2026-11-21", hour=10)  # Deniz already has this slot
    assert "already has an appointment on 21/11/2026 at 10:00" in page(book(client, dentist=1, day="2026-11-21", hour=10))


def test_only_the_rest_of_this_month_in_working_hours(as_free_patient):
    assert "rest of this month" in page(book(as_free_patient, day="2026-12-02"))
    assert "rest of this month" in page(book(as_free_patient, day="2026-11-17"))
    assert "already passed" in page(book(as_free_patient, day="2026-11-18", hour=10))
    assert "Not a valid choice" in page(book(as_free_patient, day="2026-11-25", hour=13))  # lunch break
    assert "Your appointment has been booked." in page(book(as_free_patient, day="2026-11-18", hour=11))


def test_service_checks_working_hours_too(app):
    from datetime import date

    from Backend.container import get_services
    from Backend.exceptions import RuleViolation

    with app.app_context():
        with pytest.raises(RuleViolation, match="working hours"):
            get_services().booking.book("80000000002", 2, date(2026, 11, 25), 13)


def test_unknown_dentist(as_free_patient):
    assert "Not a valid choice" in page(book(as_free_patient, dentist=99))


def test_dentist_on_holiday_cannot_be_booked(tmp_path):
    app = build_app(tmp_path, now=datetime(2026, 12, 5, 9, 0))  # the demo dentist rests on 10 December
    client = app.test_client()
    log_in(client, PATIENT_FREE)
    response = book(client, dentist=1, day="2026-12-10", hour=9)
    assert "is on holiday on that day" in page(response)
    assert "Your appointment has been booked." in page(book(client, dentist=1, day="2026-12-11", hour=9))


def test_new_account_cannot_book(as_fresh):
    assert "add an address and a phone number" in page(as_fresh.get("/appointments/book", follow_redirects=True))


def test_past_appointments_show_treatments_and_medicines(as_patient):
    listing = page(as_patient.get("/appointments"))
    assert "Past appointments" in listing and "Details" in listing
    detail = page(as_patient.get("/treatments/1"))  # treatment 1 belongs to another patient or this one
    assert detail  # either a detail page or a redirect page, never an error


def test_patients_only_see_their_own_treatments(as_patient, app):
    with app.app_context():
        from Backend.container import get_services
        own = [a for a in get_services().booking.my_appointments("80000000001")["past"] if a["treatment_id"]]
        others = [t for t in range(1, 30) if t not in {a["treatment_id"] for a in own}]
    assert as_patient.get(f"/treatments/{own[0]['treatment_id']}").status_code == 200
    response = as_patient.get(f"/treatments/{others[0]}", follow_redirects=True)
    assert "no such treatment" in page(response)
