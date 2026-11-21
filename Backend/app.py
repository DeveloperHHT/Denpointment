"""The application factory."""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect

from . import database
from .catalog import complaint_label
from .clock import Clock
from .config import ROOT, Settings
from .database import Database
from .routes import register_blueprints
from .security import current_user
from .services.auth import PasswordHasher

FRONTEND = ROOT / "Frontend"


def _version() -> str:
    version_file = ROOT / "version.py"
    if not version_file.exists():
        return ""
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', version_file.read_text())
    return match.group(1) if match else ""


def ensure_sqlite_schema(settings: Settings) -> None:
    """Creates the tables of a new SQLite database (the demo and the tests)."""
    db = Database(settings)
    try:
        exists = db.fetch_one("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'persons'")
        if not exists:
            db.run_script((ROOT / "Backend" / "Database" / "schema_sqlite.sql").read_text(encoding="utf-8"))
    finally:
        db.close()


def create_app(settings: Optional[Settings] = None, clock: Optional[Clock] = None) -> Flask:
    settings = settings or Settings.from_environment()
    app = Flask(__name__, template_folder=str(FRONTEND / "templates"), static_folder=str(FRONTEND / "static"))
    app.config.update(
        SETTINGS=settings,
        CLOCK=clock or Clock(),
        HASHER=PasswordHasher(settings.password_rounds),
        SECRET_KEY=settings.secret_key,
        WTF_CSRF_ENABLED=settings.csrf_enabled,
        TESTING=settings.testing,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        VERSION=_version(),
    )

    if settings.backend == "sqlite":
        ensure_sqlite_schema(settings)

    CSRFProtect(app)
    database.init_app(app)
    register_blueprints(app)
    _register_template_helpers(app)
    _register_error_handlers(app)
    _register_security_headers(app)
    return app


def _register_template_helpers(app: Flask) -> None:
    @app.context_processor
    def inject() -> dict:
        return {"current_user": current_user(), "app_version": app.config["VERSION"],
                "today": app.config["CLOCK"].today()}

    @app.template_filter("complaint")
    def complaint_filter(value: str) -> str:
        return complaint_label(value)

    @app.template_filter("hour")
    def hour_filter(value: int) -> str:
        return f"{int(value):02d}:00"

    @app.template_filter("day")
    def day_filter(value) -> str:
        """A date, or a row with year, month and day, as '21 Nov 2026'."""
        if not isinstance(value, date):
            value = date(value["year"], value["month"], value["day"])
        return f"{value.day} {value.strftime('%b')} {value.year}"

    @app.template_filter("money")
    def money_filter(value) -> str:
        return f"{float(value):,.0f}"


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, title="Page not found",
                               text="The page you are looking for does not exist."), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("error.html", code=500, title="Something went wrong",
                               text="The server could not finish your request. Please try again."), 500

    @app.errorhandler(CSRFError)
    def csrf_failed(_error):
        flash("Your form has expired. Please try again.", "warning")
        return redirect(request.referrer or url_for("auth.login"))


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def add_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "frame-ancestors 'none'; form-action 'self'")
        return response
