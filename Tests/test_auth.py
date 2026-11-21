from Tests.conftest import DENTIST, PATIENT, log_in, page


def test_login_shows_the_dashboard(client):
    response = log_in(client, PATIENT)
    assert response.status_code == 200
    assert "Hello, Deniz" in page(response)


def test_wrong_password_and_unknown_email_give_the_same_message(client):
    wrong = page(log_in(client, PATIENT, "nope"))
    unknown = page(log_in(client, "nobody@denpointment.example", "nope"))
    assert "The email or the password is wrong." in wrong
    assert "The email or the password is wrong." in unknown


def test_pages_need_a_login(client):
    response = client.get("/appointments")
    assert response.status_code == 302
    assert "/?next=" in response.headers["Location"]


def test_login_does_not_redirect_to_other_sites(client):
    response = client.post("/?next=https://evil.example/", data={"email": PATIENT, "password": "demo1234"})
    assert response.status_code == 302
    assert "evil.example" not in response.headers["Location"]
    response = client.post("/?next=//evil.example/", data={"email": PATIENT, "password": "demo1234"})
    assert "evil.example" not in response.headers["Location"]


def test_login_follows_a_local_next(client):
    response = client.post("/?next=/profile/", data={"email": PATIENT, "password": "demo1234"})
    assert response.headers["Location"].endswith("/profile/")


def test_logout_needs_post_and_ends_the_session(client):
    log_in(client, PATIENT)
    assert client.get("/logout").status_code == 405
    assert client.post("/logout").status_code == 302
    assert client.get("/dashboard").status_code == 302


def test_register_creates_an_account_that_can_log_in(client):
    data = {"ssn": "70000000001", "email": "new@denpointment.example", "first_name": "Mia", "last_name": "Lund",
            "gender": "female", "birth_date": "1990-03-04", "password": "secret1", "confirm": "secret1"}
    response = client.post("/register", data=data, follow_redirects=True)
    assert "Your account has been created" in page(response)
    assert "Hello, Mia" in page(log_in(client, "new@denpointment.example", "secret1"))


def test_register_rejects_duplicates_and_bad_input(client):
    base = {"ssn": "70000000002", "email": "other@denpointment.example", "first_name": "Mia", "last_name": "Lund",
            "gender": "female", "birth_date": "1990-03-04", "password": "secret1", "confirm": "secret1"}
    assert "SSN has already" in page(client.post("/register", data={**base, "ssn": "80000000001"}))
    assert "email has already" in page(client.post("/register", data={**base, "email": PATIENT}))
    assert "do not match" in page(client.post("/register", data={**base, "confirm": "different"}))
    assert "digits only" in page(client.post("/register", data={**base, "ssn": "12345abcde"}))
    assert "cannot be in the future" in page(client.post("/register", data={**base, "birth_date": "2030-01-01"}))


def test_roles_come_from_the_database(client):
    assert "Today&#39;s appointments" in page(log_in(client, DENTIST))
