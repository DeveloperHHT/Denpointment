import re

from Tests.conftest import PATIENT, log_in, page

def waiting_appointment_ids(client):
    """Ids of today's appointments that still wait for a treatment."""
    return re.findall(r"/dentist/appointments/(\d+)/treatment", page(client.get("/dentist/appointments/today")))


TREATMENT = {"action": "dental filling", "complaint": "toothache", "charge": "150", "description": "x-ray"}


def test_patients_cannot_open_dentist_pages(as_patient):
    for url in ("/dentist/appointments/today", "/dentist/appointments/upcoming", "/dentist/treatments",
                "/dentist/holidays", "/dentist/statistics", "/dentist/patients/2"):
        response = as_patient.get(url)
        assert response.status_code == 302 and response.headers["Location"].endswith("/dashboard"), url


def test_dentist_pages_render(as_dentist):
    assert "09:00" in page(as_dentist.get("/dentist/appointments/today"))
    assert "Patient profile" in page(as_dentist.get("/dentist/appointments/upcoming"))
    assert "Treatment history" in page(as_dentist.get("/dentist/treatments"))
    assert "Statistics" in page(as_dentist.get("/dentist/statistics"))


def test_treatment_for_todays_appointment_with_medicines(as_dentist):
    today = page(as_dentist.get("/dentist/appointments/today"))
    assert "Add treatment" in today
    # the second appointment of today (appointment id is found from the link)
    link = waiting_appointment_ids(as_dentist)[0]
    response = as_dentist.post(f"/dentist/appointments/{link}/treatment", data=TREATMENT, follow_redirects=True)
    assert "The treatment has been saved" in page(response)
    again = as_dentist.post(f"/dentist/appointments/{link}/treatment", data=TREATMENT, follow_redirects=True)
    assert "Edit treatment" in page(again)  # an appointment has one treatment, so it opens the edit form

    treatment_id = [int(part) for part in response.request.path.split("/") if part.isdigit()][0]
    as_dentist.post(f"/dentist/treatments/{treatment_id}/medicines", data={"medicine_name": "Paracetamol 500 mg"})
    assert "Paracetamol 500 mg" in page(as_dentist.get(f"/dentist/treatments/{treatment_id}/medicines"))
    duplicate = as_dentist.post(f"/dentist/treatments/{treatment_id}/medicines", data={"medicine_name": "paracetamol 500 mg"})
    assert "already on the list" in page(duplicate)
    as_dentist.post(f"/dentist/treatments/{treatment_id}/medicines/{_medicine_id(as_dentist, treatment_id)}/delete")
    assert "Paracetamol 500 mg" not in page(as_dentist.get(f"/dentist/treatments/{treatment_id}/medicines"))


def _medicine_id(client, treatment_id):
    html = page(client.get(f"/dentist/treatments/{treatment_id}/medicines"))
    return html.split(f"/medicines/")[1].split("/delete")[0]


def test_treatment_can_be_edited(as_dentist):
    today = page(as_dentist.get("/dentist/appointments/today"))
    treatment_id = today.split("/dentist/treatments/")[1].split("/")[0]  # the first appointment already has one
    response = as_dentist.post(f"/dentist/treatments/{treatment_id}/edit", data={**TREATMENT, "charge": "999"},
                               follow_redirects=True)
    assert "The treatment has been updated." in page(response)
    assert 'value="999"' in page(as_dentist.get(f"/dentist/treatments/{treatment_id}/edit"))


def test_treatment_rules(as_dentist):
    assert "only record a treatment for today" in page(
        as_dentist.post("/dentist/appointments/1/treatment", data=TREATMENT, follow_redirects=True))
    assert "no such appointment" in page(
        as_dentist.get("/dentist/appointments/9999/treatment", follow_redirects=True))
    waiting = waiting_appointment_ids(as_dentist)[0]
    assert "Please enter the charge" in page(
        as_dentist.post(f"/dentist/appointments/{waiting}/treatment", data={**TREATMENT, "charge": ""}))
    assert "Please enter a sensible charge" in page(
        as_dentist.post(f"/dentist/appointments/{waiting}/treatment", data={**TREATMENT, "charge": "-5"}))


def test_dentist_cannot_touch_treatments_of_a_colleague(client, app):
    with app.app_context():
        from Backend.database import get_database
        row = get_database().fetch_one("SELECT treatment_id FROM treatments WHERE treator_id = 2 LIMIT 1")
    log_in(client, "dentist@denpointment.example")
    response = client.get(f"/dentist/treatments/{row['treatment_id']}/medicines", follow_redirects=True)
    assert "no such treatment" in page(response)


def test_history_can_be_searched_by_date(as_dentist):
    listing = page(as_dentist.get("/dentist/treatments"))
    assert "Treatment history" in listing
    empty = page(as_dentist.get("/dentist/treatments?date=2020-01-01"))
    assert "No appointments on that day" in empty


def test_holiday_rules(as_dentist):
    assert "next month" in page(as_dentist.post("/dentist/holidays/add", data={"date": "2026-11-25", "reason": "x"}))
    assert "next month" in page(as_dentist.post("/dentist/holidays/add", data={"date": "2027-01-05", "reason": "x"}))
    assert "already been registered" in page(as_dentist.post("/dentist/holidays/add", data={"date": "2026-12-10"}))
    assert "The holiday has been added." in page(
        as_dentist.post("/dentist/holidays/add", data={"date": "2026-12-20", "reason": "Trip"}, follow_redirects=True))
    assert "at most 3 days" in page(as_dentist.post("/dentist/holidays/add", data={"date": "2026-12-22"}))
    assert "25 characters" in page(as_dentist.post("/dentist/holidays/add", data={"date": "2026-12-23", "reason": "x" * 26}))


def test_holiday_delete_rules(as_dentist):
    listing = page(as_dentist.get("/dentist/holidays"))
    assert "Conference" in listing and "Family visit" in listing
    # holiday 1 is the one 30 days in the past, 2 and 3 are in December
    assert "Delete the holiday" in listing
    ok = as_dentist.post("/dentist/holidays/2/delete", follow_redirects=True)
    assert "The holiday has been deleted." in page(ok)
    gone = as_dentist.post("/dentist/holidays/1/delete", follow_redirects=True)
    assert "cannot delete a holiday" in page(gone)
    assert "no such holiday" in page(as_dentist.post("/dentist/holidays/99/delete", follow_redirects=True))


def test_holidays_are_changed_with_post_only(as_dentist):
    assert as_dentist.get("/dentist/holidays/2/delete").status_code == 405


def test_patient_profile_only_for_own_patients(as_dentist):
    assert "Deniz" in page(as_dentist.get("/dentist/patients/1"))
    # Oscar (patient 5) has an upcoming appointment with this dentist, Ada (4) as well; patients 3-5 have visited dentist 1
    response = as_dentist.get("/dentist/patients/999", follow_redirects=True)
    assert "no such patient" in page(response)


def test_statistics_numbers(as_dentist):
    html = page(as_dentist.get("/dentist/statistics"))
    assert "Most expensive treatment" in html and "900" in html
    assert "No data" not in html.split("Average charge")[1].split("Most expensive")[0]
