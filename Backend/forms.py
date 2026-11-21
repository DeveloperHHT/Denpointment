"""Flask-WTF forms. They only check the shape of the input; the rules of the clinic live in the services."""
from __future__ import annotations

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, PasswordField, SelectField, StringField
from wtforms.validators import (DataRequired, Email, EqualTo, InputRequired, Length, NumberRange, Regexp,
                                ValidationError)

DIGITS = Regexp(r"^[0-9]+$", message="Please enter digits only.")


def _strip(value):
    """Text fields arrive as None when they are not sent at all; they become an empty string."""
    return (value or "").strip()


def _not_in_future(_form, field) -> None:
    if field.data and field.data > date.today():
        raise ValidationError("The birth date cannot be in the future.")


class RegistrationForm(FlaskForm):
    ssn = StringField("SSN", filters=[_strip], validators=[DataRequired("Please enter your SSN."), Length(min=10, max=15), DIGITS])
    email = StringField("Email", filters=[_strip], validators=[DataRequired("Please enter your email."), Length(max=50),
                                             Email("Please enter a valid email.")])
    first_name = StringField("First name", filters=[_strip], validators=[DataRequired("Please enter your first name."),
                                                       Length(min=2, max=50)])
    last_name = StringField("Last name", filters=[_strip], validators=[DataRequired("Please enter your last name."),
                                                     Length(min=2, max=50)])
    gender = SelectField("Gender", choices=[("female", "Female"), ("male", "Male")],
                         validators=[DataRequired("Please select your gender.")])
    birth_date = DateField("Birth date", format="%Y-%m-%d",
                           validators=[DataRequired("Please enter your birth date."), _not_in_future])
    password = PasswordField("Password", validators=[DataRequired("Please type a password."), Length(min=6, max=72),
                                                     EqualTo("confirm", message="The passwords do not match.")])
    confirm = PasswordField("Repeat the password")


class LoginForm(FlaskForm):
    email = StringField("Email", filters=[_strip], validators=[DataRequired("Please enter your email."), Email("Please enter a valid email.")])
    password = PasswordField("Password", validators=[DataRequired("Please type your password.")])


class PhoneForm(FlaskForm):
    contact_number = StringField("Phone number", filters=[_strip], validators=[DataRequired("Please enter a phone number."),
                                                             Length(min=10, max=15), DIGITS])


class AddressForm(FlaskForm):
    city = StringField("City", filters=[_strip], validators=[DataRequired("Please enter the city."), Length(min=2, max=20)])
    street = StringField("Street", filters=[_strip], validators=[DataRequired("Please enter the street."), Length(min=2, max=20)])
    zip_code = StringField("ZIP code", filters=[_strip], validators=[DataRequired("Please enter the ZIP code."),
                                                   Length(min=3, max=10), DIGITS])


class ChronicDiseaseForm(FlaskForm):
    chronic_disease = StringField("Chronic disease", filters=[_strip], validators=[DataRequired("Please enter the disease."),
                                                                 Length(min=3, max=50)])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Current password", validators=[DataRequired("Please enter your current password.")])
    password = PasswordField("New password", validators=[DataRequired("Please type a new password."),
                                                         Length(min=6, max=72),
                                                         EqualTo("confirm", message="The passwords do not match.")])
    confirm = PasswordField("Repeat the new password")


class ChangeEmailForm(FlaskForm):
    email = StringField("New email", filters=[_strip], validators=[DataRequired("Please enter the new email."), Length(max=50),
                                                 Email("Please enter a valid email.")])
    password = PasswordField("Password", validators=[DataRequired("Please type your password.")])


class BookAppointmentForm(FlaskForm):
    dentist = SelectField("Dentist", coerce=int, validators=[InputRequired("Please select a dentist.")])
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired("Please choose a date.")])
    hour = SelectField("Hour", coerce=int, validators=[InputRequired("Please select an hour.")])


class AddHolidayForm(FlaskForm):
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired("Please choose a date.")])
    reason = StringField("Reason (optional)", filters=[_strip], validators=[Length(max=25, message="The reason can have 25 characters at most.")])


class TreatmentForm(FlaskForm):
    action = StringField("Action", filters=[_strip], validators=[DataRequired("Please enter the action."), Length(min=3, max=25)])
    complaint = StringField("Complaint", filters=[_strip], validators=[DataRequired("Please enter the complaint."), Length(min=3, max=25)])
    charge = IntegerField("Charge", validators=[InputRequired("Please enter the charge."),
                                                NumberRange(min=0, max=1_000_000, message="Please enter a sensible charge.")])
    description = StringField("Note (optional)", filters=[_strip], validators=[Length(max=50, message="The note can have 50 characters at most.")])


class MedicineForm(FlaskForm):
    medicine_name = StringField("Medicine", filters=[_strip], validators=[DataRequired("Please enter the medicine."), Length(min=2, max=50)])


class SearchTreatmentForm(FlaskForm):
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired("Please choose a date.")])


class ActionForm(FlaskForm):
    """An empty form: it only carries the CSRF token of buttons that change data (delete, ...)."""
