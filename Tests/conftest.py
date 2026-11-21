"""Shared fixtures: a demo database in a temporary folder and a clock that stands still."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Backend.app import create_app  # noqa: E402
from Backend.clock import FixedClock  # noqa: E402
from Backend.config import Settings  # noqa: E402
from Scripts.seed_demo import PASSWORD, prepare_demo_database  # noqa: E402

NOW = datetime(2026, 11, 18, 10, 30)  # a Wednesday, 10:30
PATIENT = "patient@denpointment.example"  # Deniz: has an upcoming appointment
PATIENT_FREE = "patient2@denpointment.example"  # Selin: can book
FRESH = "fresh@denpointment.example"  # no address and no phone yet
DENTIST = "dentist@denpointment.example"  # Elif: dentist id 1


def build_app(directory: Path, now: datetime = NOW, csrf: bool = False):
    settings = Settings(backend="sqlite", sqlite_path=directory / "test.db", csrf_enabled=csrf, testing=True,
                        secret_key="test-key", password_rounds=1000)
    prepare_demo_database(settings, today=NOW.date(), rounds=1000)
    return create_app(settings, FixedClock(now))


@pytest.fixture()
def app(tmp_path):
    return build_app(tmp_path)


@pytest.fixture()
def client(app):
    return app.test_client()


def log_in(client, email: str, password: str = PASSWORD):
    return client.post("/", data={"email": email, "password": password}, follow_redirects=True)


@pytest.fixture()
def as_patient(client):
    log_in(client, PATIENT)
    return client


@pytest.fixture()
def as_free_patient(client):
    log_in(client, PATIENT_FREE)
    return client


@pytest.fixture()
def as_dentist(client):
    log_in(client, DENTIST)
    return client


@pytest.fixture()
def as_fresh(client):
    log_in(client, FRESH)
    return client


def page(response) -> str:
    return response.get_data(as_text=True)
