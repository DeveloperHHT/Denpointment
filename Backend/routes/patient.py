"""Pages for patients: booking and looking at their appointments and treatments."""
from __future__ import annotations

import calendar

from flask import Blueprint, flash, redirect, render_template, url_for

from ..container import get_services
from ..exceptions import RuleViolation
from ..forms import BookAppointmentForm
from ..security import current_user, patient_required
from ..services.booking import HOURS

bp = Blueprint("patient", __name__)


@bp.route("/appointments")
@patient_required
def appointments():
    overview = get_services().booking.my_appointments(current_user()["ssn"])
    return render_template("patient/appointments.html", **overview)


@bp.route("/appointments/book", methods=["GET", "POST"])
@patient_required
def book():
    services = get_services()
    ssn = current_user()["ssn"]
    today = services.booking.clock.today()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    form = BookAppointmentForm()
    dentists = services.persons.dentists()
    form.dentist.choices = [(d["dentist_id"], f"{d['first_name']} {d['last_name']}") for d in dentists]
    form.hour.choices = [(hour, f"{hour:02d}:00") for hour in HOURS]

    if services.booking.has_upcoming(ssn):
        flash("You already have an upcoming appointment. You can book another one after it.", "warning")
        return redirect(url_for("patient.appointments"))

    if form.validate_on_submit():
        try:
            services.booking.book(ssn, form.dentist.data, form.date.data, form.hour.data)
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("Your appointment has been booked.", "success")
            return redirect(url_for("patient.appointments"))
    elif not form.is_submitted():
        form.date.data = today
    return render_template("patient/book.html", form=form, dentists=dentists, first_day=today, last_day=last_day)


@bp.route("/treatments/<int:treatment_id>")
@patient_required
def treatment(treatment_id: int):
    try:
        details = get_services().treatments.for_patient(current_user()["ssn"], treatment_id)
    except RuleViolation as error:
        flash(error.message, error.category)
        return redirect(url_for("patient.appointments"))
    return render_template("patient/treatment.html", **details)
