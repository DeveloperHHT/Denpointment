"""Who is logged in and which pages they may open."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Optional

from flask import flash, g, redirect, request, session, url_for

from .container import get_services


def current_user() -> Optional[Dict[str, Any]]:
    """The logged-in person. Roles are read again on every request, so becoming a patient needs no new login."""
    if "user" not in g:
        g.user = None
        ssn = session.get("ssn")
        if ssn:
            person = get_services().persons.find_by_ssn(ssn)
            if person is None:
                session.clear()
            else:
                g.user = get_services().auth.session_data(person)
    return g.user


def log_in(user: Dict[str, Any]) -> None:
    session.clear()  # a new session id after login, so an old one cannot be reused
    session["ssn"] = user["ssn"]
    session.permanent = False


def log_out() -> None:
    session.clear()


def _guard(allowed: Callable[[Dict[str, Any]], bool], message: str) -> Callable:
    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapper(*args: Any, **kwargs: Any):
            user = current_user()
            if user is None:
                flash("Please log in to see this page.", "danger")
                return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
            if not allowed(user):
                flash(message, "danger")
                return redirect(url_for("auth.dashboard"))
            return view(*args, **kwargs)
        return wrapper
    return decorator


login_required = _guard(lambda user: True, "")
patient_required = _guard(lambda user: user["is_patient"],
                          "Please add an address and a phone number to your profile first.")
dentist_required = _guard(lambda user: user["is_dentist"], "You are not authorized!")
