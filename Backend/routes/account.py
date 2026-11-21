"""The logged-in person's own profile: contact data, chronic diseases, password and email."""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..container import get_services
from ..exceptions import RuleViolation
from ..forms import (ActionForm, AddressForm, ChangeEmailForm, ChangePasswordForm, ChronicDiseaseForm,
                     PhoneForm)
from ..security import current_user, login_required

bp = Blueprint("account", __name__, url_prefix="/profile")


def _back_to_profile():
    return redirect(url_for("account.profile"))


@bp.route("/")
@login_required
def profile():
    user = current_user()
    overview = get_services().profile.overview(user["ssn"])
    return render_template("account/profile.html", delete_form=ActionForm(), **overview)


def _after_change(message: str):
    """Flashes the message; a person with an address and a phone number becomes a patient."""
    flash(message, "success")
    if get_services().profile.activate_patient_if_ready(current_user()["ssn"]):
        flash("Your account is active now. You can book appointments.", "success")
    return _back_to_profile()


# -- password and email -----------------------------------------------------------------------

@bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            get_services().auth.change_password(current_user()["ssn"], form.old_password.data, form.password.data)
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("Your password has been changed.", "success")
            return _back_to_profile()
    return render_template("account/change_password.html", form=form)


@bp.route("/email", methods=["GET", "POST"])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        try:
            get_services().auth.change_email(current_user()["ssn"], form.email.data.strip(), form.password.data)
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            flash("Your email has been changed.", "success")
            return _back_to_profile()
    return render_template("account/change_email.html", form=form)


# -- addresses --------------------------------------------------------------------------------

@bp.route("/addresses/add", methods=["GET", "POST"])
@login_required
def add_address():
    form = AddressForm()
    if form.validate_on_submit():
        try:
            get_services().profile.add_address(current_user()["ssn"], form.city.data.strip(),
                                               form.street.data.strip(), form.zip_code.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            return _after_change("The address has been added.")
    return render_template("account/address_form.html", form=form, editing=False)


@bp.route("/addresses/<int:address_id>/edit", methods=["GET", "POST"])
@login_required
def edit_address(address_id: int):
    profile = get_services().profile
    ssn = current_user()["ssn"]
    try:
        address = profile.get_address(ssn, address_id)
    except RuleViolation as error:
        flash(error.message, error.category)
        return _back_to_profile()
    form = AddressForm(data=address)
    if form.validate_on_submit():
        try:
            profile.update_address(ssn, address_id, form.city.data.strip(), form.street.data.strip(),
                                   form.zip_code.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            return _after_change("The address has been updated.")
    return render_template("account/address_form.html", form=form, editing=True)


@bp.route("/addresses/<int:address_id>/delete", methods=["POST"])
@login_required
def delete_address(address_id: int):
    if ActionForm().validate_on_submit():
        try:
            get_services().profile.delete_address(current_user()["ssn"], address_id)
            flash("The address has been deleted.", "success")
        except RuleViolation as error:
            flash(error.message, error.category)
    return _back_to_profile()


# -- phone numbers ----------------------------------------------------------------------------

@bp.route("/phones/add", methods=["GET", "POST"])
@login_required
def add_phone():
    form = PhoneForm()
    if form.validate_on_submit():
        try:
            get_services().profile.add_phone(current_user()["ssn"], form.contact_number.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            return _after_change("The phone number has been added.")
    return render_template("account/phone_form.html", form=form, editing=False)


@bp.route("/phones/<number>/edit", methods=["GET", "POST"])
@login_required
def edit_phone(number: str):
    profile = get_services().profile
    ssn = current_user()["ssn"]
    try:
        phone = profile.get_phone(ssn, number)
    except RuleViolation as error:
        flash(error.message, error.category)
        return _back_to_profile()
    form = PhoneForm(data={"contact_number": phone["contact_number"]})
    if form.validate_on_submit():
        try:
            profile.update_phone(ssn, number, form.contact_number.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            return _after_change("The phone number has been updated.")
    return render_template("account/phone_form.html", form=form, editing=True)


@bp.route("/phones/<number>/delete", methods=["POST"])
@login_required
def delete_phone(number: str):
    if ActionForm().validate_on_submit():
        try:
            get_services().profile.delete_phone(current_user()["ssn"], number)
            flash("The phone number has been deleted.", "success")
        except RuleViolation as error:
            flash(error.message, error.category)
    return _back_to_profile()


# -- chronic diseases -------------------------------------------------------------------------

@bp.route("/chronic-diseases/add", methods=["GET", "POST"])
@login_required
def add_chronic_disease():
    form = ChronicDiseaseForm()
    if form.validate_on_submit():
        try:
            get_services().profile.add_chronic_disease(current_user()["ssn"], form.chronic_disease.data.strip())
        except RuleViolation as error:
            flash(error.message, error.category)
        else:
            return _after_change("The chronic disease has been added.")
    return render_template("account/chronic_disease_form.html", form=form)


@bp.route("/chronic-diseases/delete", methods=["POST"])
@login_required
def delete_chronic_disease():
    if ActionForm().validate_on_submit():
        try:
            get_services().profile.delete_chronic_disease(current_user()["ssn"],
                                                          request.form.get("chronic_disease", "").strip())
            flash("The chronic disease has been deleted.", "success")
        except RuleViolation as error:
            flash(error.message, error.category)
    return _back_to_profile()
