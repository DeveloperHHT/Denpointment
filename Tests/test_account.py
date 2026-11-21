from Tests.conftest import PATIENT, PATIENT_FREE, log_in, page


def test_new_account_becomes_a_patient_after_address_and_phone(as_fresh):
    assert as_fresh.get("/appointments", follow_redirects=True).status_code == 200
    assert "add an address and a phone number" in page(as_fresh.get("/appointments", follow_redirects=True))

    response = as_fresh.post("/profile/addresses/add", data={"city": "Rize", "street": "Tea Road", "zip_code": "53000"},
                             follow_redirects=True)
    assert "The address has been added." in page(response)
    assert "Your account is active" not in page(response)  # a phone number is still missing

    response = as_fresh.post("/profile/phones/add", data={"contact_number": "5551234567"}, follow_redirects=True)
    assert "Your account is active now" in page(response)
    assert as_fresh.get("/appointments").status_code == 200


def test_the_last_address_and_phone_cannot_be_deleted(as_patient):
    profile = page(as_patient.get("/profile/"))
    assert "Elm Street" in profile
    response = as_patient.post("/profile/addresses/1/delete", follow_redirects=True)
    assert "You need at least one address" in page(response)
    response = as_patient.post("/profile/phones/5550000001/delete", follow_redirects=True)
    assert "You need at least one phone number" in page(response)


def test_address_can_be_added_edited_and_deleted(as_patient):
    as_patient.post("/profile/addresses/add", data={"city": "Rize", "street": "Tea Road", "zip_code": "53000"})
    assert "Tea Road" in page(as_patient.get("/profile/"))
    duplicate = as_patient.post("/profile/addresses/add", data={"city": "Rize", "street": "Tea Road", "zip_code": "53000"})
    assert "already in your profile" in page(duplicate)
    as_patient.post("/profile/addresses/6/edit", data={"city": "Rize", "street": "Sea Road", "zip_code": "53000"})
    profile = page(as_patient.get("/profile/"))
    assert "Sea Road" in profile and "Tea Road" not in profile
    as_patient.post("/profile/addresses/6/delete")
    assert "Sea Road" not in page(as_patient.get("/profile/"))


def test_other_peoples_addresses_are_not_reachable(as_patient):
    # address 2 belongs to Selin
    assert "no such address" in page(as_patient.get("/profile/addresses/2/edit", follow_redirects=True))
    assert "no such address" in page(as_patient.post("/profile/addresses/2/delete", follow_redirects=True))


def test_phone_numbers_are_unique_and_validated(as_patient):
    assert "already been registered" in page(as_patient.post("/profile/phones/add", data={"contact_number": "5550000002"}))
    assert "digits only" in page(as_patient.post("/profile/phones/add", data={"contact_number": "55-500-00"}))
    as_patient.post("/profile/phones/add", data={"contact_number": "5559990000"})
    as_patient.post("/profile/phones/5559990000/edit", data={"contact_number": "5559990001"})
    profile = page(as_patient.get("/profile/"))
    assert "5559990001" in profile and "5559990000" not in profile


def test_chronic_diseases_can_be_added_and_removed(as_patient):
    as_patient.post("/profile/chronic-diseases/add", data={"chronic_disease": "high blood pressure"})
    assert "high blood pressure" in page(as_patient.get("/profile/"))
    assert "already in your profile" in page(
        as_patient.post("/profile/chronic-diseases/add", data={"chronic_disease": "high blood pressure"}))
    as_patient.post("/profile/chronic-diseases/delete", data={"chronic_disease": "high blood pressure"})
    assert "high blood pressure" not in page(as_patient.get("/profile/"))


def test_password_change(client):
    log_in(client, PATIENT)
    bad = client.post("/profile/password", data={"old_password": "wrong", "password": "newpass1", "confirm": "newpass1"})
    assert "current password is wrong" in page(bad)
    same = client.post("/profile/password", data={"old_password": "demo1234", "password": "demo1234", "confirm": "demo1234"})
    assert "cannot be the same" in page(same)
    ok = client.post("/profile/password", data={"old_password": "demo1234", "password": "newpass1", "confirm": "newpass1"},
                     follow_redirects=True)
    assert "Your password has been changed." in page(ok)
    client.post("/logout")
    assert "Hello, Deniz" in page(log_in(client, PATIENT, "newpass1"))


def test_email_change(client):
    log_in(client, PATIENT)
    assert "password is wrong" in page(client.post("/profile/email", data={"email": "x@denpointment.example", "password": "no"}))
    assert "already been registered" in page(
        client.post("/profile/email", data={"email": PATIENT_FREE, "password": "demo1234"}))
    ok = client.post("/profile/email", data={"email": "deniz@denpointment.example", "password": "demo1234"},
                     follow_redirects=True)
    assert "Your email has been changed." in page(ok)
    client.post("/logout")
    assert "Hello, Deniz" in page(log_in(client, "deniz@denpointment.example"))
