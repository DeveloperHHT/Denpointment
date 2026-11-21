"""Login, registration and the home page after login."""
from __future__ import annotations

from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..container import get_services
from ..exceptions import RuleViolation
from ..forms import LoginForm, RegistrationForm
from ..security import current_user, log_in, log_out, login_required

bp = Blueprint("auth", __name__)


def _safe_next(target: str):
    """Only paths on this site are allowed as the place to go after login."""
    parts = urlparse(target or "")
    if target and not parts.scheme and not parts.netloc and target.startswith("/") and not target.startswith("//"):
        return target
    return None


@bp.route("/", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("auth.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            log_in(get_services().auth.authenticate(form.email.data.strip(), form.password.data))
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("Welcome back!", "success")
            return redirect(_safe_next(request.args.get("next", "")) or url_for("auth.dashboard"))
    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("auth.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            get_services().auth.register(
                form.ssn.data.strip(), form.email.data.strip(), form.password.data, form.first_name.data.strip(),
                form.last_name.data.strip(), form.gender.data, form.birth_date.data)
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("Your account has been created. Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp.route("/dashboard")
@login_required
def dashboard():
    services = get_services()
    user = current_user()
    context = {"next_appointment": None, "today_count": 0, "upcoming_count": 0}
    if user["is_patient"]:
        upcoming = services.booking.my_appointments(user["ssn"])["upcoming"]
        context["next_appointment"] = upcoming[0] if upcoming else None
    if user["is_dentist"]:
        context["today_count"] = len(services.treatments.today(user["ssn"]))
        context["upcoming_count"] = len(services.treatments.upcoming(user["ssn"]))
    return render_template("dashboard.html", **context)


@bp.route("/logout", methods=["POST"])
def logout():
    log_out()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
