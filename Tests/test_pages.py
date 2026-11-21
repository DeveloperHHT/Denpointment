"""Every page opens without an error for the roles that may see it."""
import pytest

from Tests.conftest import page

PUBLIC = ["/", "/register"]
ANY_USER = ["/dashboard", "/profile/", "/profile/password", "/profile/email", "/profile/addresses/add",
            "/profile/phones/add", "/profile/chronic-diseases/add"]
PATIENT_PAGES = ["/appointments", "/appointments/book"]
DENTIST_PAGES = ["/dentist/appointments/today", "/dentist/appointments/upcoming", "/dentist/treatments",
                 "/dentist/holidays", "/dentist/holidays/add", "/dentist/statistics", "/dentist/patients/1",
                 "/dentist/treatments?date=2026-11-01"]


@pytest.mark.parametrize("url", PUBLIC)
def test_public_pages(client, url):
    assert client.get(url).status_code == 200


@pytest.mark.parametrize("url", ANY_USER + PATIENT_PAGES)
def test_patient_pages(as_free_patient, url):
    assert as_free_patient.get(url).status_code == 200


@pytest.mark.parametrize("url", ANY_USER + DENTIST_PAGES)
def test_dentist_pages(as_dentist, url):
    assert as_dentist.get(url).status_code == 200


@pytest.mark.parametrize("url", ANY_USER)
def test_pages_of_a_new_account(as_fresh, url):
    assert as_fresh.get(url).status_code == 200


def test_edit_forms_open(as_patient):
    assert as_patient.get("/profile/addresses/1/edit").status_code == 200
    assert as_patient.get("/profile/phones/5550000001/edit").status_code == 200


def test_not_found_page(client):
    response = client.get("/there-is-nothing-here")
    assert response.status_code == 404 and "Page not found" in page(response)


def test_security_headers(client):
    headers = client.get("/").headers
    assert headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
