from Tests.conftest import DENTIST, PATIENT, build_app, page


def test_forms_without_a_token_are_refused(tmp_path):
    app = build_app(tmp_path, csrf=True)
    client = app.test_client()
    response = client.post("/", data={"email": PATIENT, "password": "demo1234"}, follow_redirects=True)
    assert "Your form has expired" in page(response)
    assert "Hello, Deniz" not in page(response)


def test_login_form_carries_a_token_and_works(tmp_path):
    app = build_app(tmp_path, csrf=True)
    client = app.test_client()
    html = page(client.get("/"))
    token = html.split('name="csrf_token" type="hidden" value="')[1].split('"')[0]
    response = client.post("/", data={"email": PATIENT, "password": "demo1234", "csrf_token": token}, follow_redirects=True)
    assert "Hello, Deniz" in page(response)


def test_delete_buttons_are_refused_without_a_token(tmp_path):
    app = build_app(tmp_path, csrf=True)
    client = app.test_client()
    with client.session_transaction() as session:
        session["ssn"] = "90000000001"
    response = client.post("/dentist/holidays/2/delete", follow_redirects=True)
    assert "Your form has expired" in page(response)
    with app.app_context():
        from Backend.database import get_database
        assert get_database().fetch_one("SELECT holiday_id FROM holiday_dates WHERE holiday_id = 2") is not None
