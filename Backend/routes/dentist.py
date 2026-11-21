"""Pages for dentists: schedule, holidays, treatments, patients and statistics."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..catalog import ACTIONS, COMPLAINTS
from ..container import get_services
from ..exceptions import RuleViolation
from ..forms import ActionForm, AddHolidayForm, MedicineForm, SearchTreatmentForm, TreatmentForm
from ..security import current_user, dentist_required

bp = Blueprint("dentist", __name__, url_prefix="/dentist")


def _go(endpoint: str, **values):
    return redirect(url_for(endpoint, **values))


# -- schedule ---------------------------------------------------------------------------------

@bp.route("/appointments/upcoming")
@dentist_required
def upcoming_appointments():
    appointments = get_services().treatments.upcoming(current_user()["ssn"])
    return render_template("dentist/upcoming.html", appointments=appointments)


@bp.route("/appointments/today")
@dentist_required
def todays_appointments():
    services = get_services()
    appointments = services.treatments.today(current_user()["ssn"])
    return render_template("dentist/today.html", appointments=appointments, today=services.treatments.clock.today())


@bp.route("/treatments")
@dentist_required
def history():
    services = get_services()
    form = SearchTreatmentForm(meta={"csrf": False}, formdata=request.args or None)
    appointments = services.treatments.history(current_user()["ssn"])
    searched = None
    if request.args.get("date") and form.validate():
        searched = form.date.data
        appointments = [a for a in appointments if (a["year"], a["month"], a["day"]) ==
                        (searched.year, searched.month, searched.day)]
    return render_template("dentist/history.html", appointments=appointments, form=form, searched=searched)


# -- treatments -------------------------------------------------------------------------------

@bp.route("/appointments/<int:appointment_id>/treatment", methods=["GET", "POST"])
@dentist_required
def add_treatment(appointment_id: int):
    services = get_services()
    ssn = current_user()["ssn"]
    try:
        context = services.treatments.appointment_with_patient(ssn, appointment_id)
    except RuleViolation as error:
        flash(error.message, error.category)
        return _go("dentist.todays_appointments")
    if context["treatment"] is not None:
        return _go("dentist.edit_treatment", treatment_id=context["treatment"]["treatment_id"])
    form = TreatmentForm()
    if form.validate_on_submit():
        try:
            treatment_id = services.treatments.add(ssn, appointment_id, form.action.data.strip(),
                                                   form.complaint.data.strip(), form.charge.data,
                                                   form.description.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("The treatment has been saved. You can add medicines now.", "success")
            return _go("dentist.medicines", treatment_id=treatment_id)
    return render_template("dentist/treatment_form.html", form=form, editing=False, actions=ACTIONS,
                           complaints=COMPLAINTS, patient=context["patient"], appointment=context["appointment"])


@bp.route("/treatments/<int:treatment_id>/edit", methods=["GET", "POST"])
@dentist_required
def edit_treatment(treatment_id: int):
    services = get_services()
    ssn = current_user()["ssn"]
    try:
        details = services.treatments.get(ssn, treatment_id)
    except RuleViolation as error:
        flash(error.message, error.category)
        return _go("dentist.history")
    treatment = details["treatment"]
    form = TreatmentForm(data=treatment)
    if form.validate_on_submit():
        try:
            services.treatments.edit(ssn, treatment_id, form.action.data.strip(), form.complaint.data.strip(),
                                     form.charge.data, form.description.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("The treatment has been updated.", "success")
            return _go("dentist.medicines", treatment_id=treatment_id)
    return render_template("dentist/treatment_form.html", form=form, editing=True, actions=ACTIONS,
                           complaints=COMPLAINTS, patient=details["patient"], appointment=treatment)


# -- medicines --------------------------------------------------------------------------------

@bp.route("/treatments/<int:treatment_id>/medicines", methods=["GET", "POST"])
@dentist_required
def medicines(treatment_id: int):
    services = get_services()
    ssn = current_user()["ssn"]
    try:
        details = services.treatments.get(ssn, treatment_id)
    except RuleViolation as error:
        flash(error.message, error.category)
        return _go("dentist.history")
    form = MedicineForm()
    if form.validate_on_submit():
        try:
            services.treatments.add_medicine(ssn, treatment_id, form.medicine_name.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("The medicine has been added.", "success")
            return _go("dentist.medicines", treatment_id=treatment_id)
    return render_template("dentist/medicines.html", form=form, delete_form=ActionForm(), **details)


@bp.route("/treatments/<int:treatment_id>/medicines/<int:medicine_id>/delete", methods=["POST"])
@dentist_required
def delete_medicine(treatment_id: int, medicine_id: int):
    if ActionForm().validate_on_submit():
        try:
            get_services().treatments.delete_medicine(current_user()["ssn"], treatment_id, medicine_id)
            flash("The medicine has been removed.", "success")
        except RuleViolation as error:
            flash(error.message, error.category)
    return _go("dentist.medicines", treatment_id=treatment_id)


# -- holidays ---------------------------------------------------------------------------------

@bp.route("/holidays")
@dentist_required
def holidays():
    overview = get_services().holidays.overview(current_user()["ssn"])
    return render_template("dentist/holidays.html", delete_form=ActionForm(), **overview)


@bp.route("/holidays/add", methods=["GET", "POST"])
@dentist_required
def add_holiday():
    services = get_services()
    form = AddHolidayForm()
    today = services.holidays.clock.today()
    if form.validate_on_submit():
        try:
            services.holidays.add(current_user()["ssn"], form.date.data, form.reason.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("The holiday has been added.", "success")
            return _go("dentist.holidays")
    return render_template("dentist/holiday_form.html", form=form, today=today)


@bp.route("/holidays/<int:holiday_id>/delete", methods=["POST"])
@dentist_required
def delete_holiday(holiday_id: int):
    if ActionForm().validate_on_submit():
        try:
            get_services().holidays.delete(current_user()["ssn"], holiday_id)
            flash("The holiday has been deleted.", "success")
        except RuleViolation as error:
            flash(error.message, error.category)
    return _go("dentist.holidays")


# -- patients and statistics ------------------------------------------------------------------

@bp.route("/patients/<int:patient_id>")
@dentist_required
def patient_profile(patient_id: int):
    try:
        overview = get_services().patients.overview(current_user()["ssn"], patient_id)
    except RuleViolation as error:
        flash(error.message, error.category)
        return _go("dentist.upcoming_appointments")
    return render_template("dentist/patient.html", **overview)


@bp.route("/statistics")
@dentist_required
def statistics():
    return render_template("dentist/statistics.html", **get_services().statistics.overview())
