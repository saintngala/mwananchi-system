"""
Flask-WTF forms for the Mwananchi System.

Using WTForms gives us CSRF protection, server-side validation, and
consistent error messages for free across every form in the app.
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, PasswordField,
    SubmitField, FloatField,
)
from wtforms.validators import (
    DataRequired, Optional, Length, Regexp, NumberRange, ValidationError,
)

from app.utils import (
    COMPLAINT_CATEGORIES, COMPLAINT_STATUSES, PROJECT_STATUSES,
    KENYA_COUNTIES, KENYAN_PHONE_REGEX,
)


class ComplaintForm(FlaskForm):
    category = SelectField(
        'Complaint Category',
        choices=[(c, c) for c in COMPLAINT_CATEGORIES],
        validators=[DataRequired(message='Please select a category.')],
    )
    description = TextAreaField(
        'Complaint Description',
        validators=[
            DataRequired(message='Please describe the issue.'),
            Length(min=10, max=2000, message='Description must be between 10 and 2000 characters.'),
        ],
    )
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    citizen_name = StringField('Your Name (optional)', validators=[Optional(), Length(max=150)])
    phone_number = StringField(
        'Phone Number (optional)',
        validators=[
            Optional(),
            Regexp(KENYAN_PHONE_REGEX, message='Enter a valid Kenyan phone number, e.g. 0712345678.'),
        ],
    )
    submit = SubmitField('Submit Complaint')


class TrackComplaintForm(FlaskForm):
    report_id = StringField(
        'Report ID',
        validators=[
            DataRequired(message='Please enter your Report ID.'),
            Length(min=5, max=20, message='That doesn\'t look like a valid Report ID.'),
        ],
    )
    submit = SubmitField('Track Complaint')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Username is required.')])
    password = PasswordField('Password', validators=[DataRequired(message='Password is required.')])
    submit = SubmitField('Login')


class ComplaintStatusForm(FlaskForm):
    status = SelectField(
        'Status',
        choices=[(s, s) for s in COMPLAINT_STATUSES],
        validators=[DataRequired()],
    )
    submit = SubmitField('Update Status')


class BudgetForm(FlaskForm):
    project_name = StringField(
        'Project Name',
        validators=[DataRequired(message='Project name is required.'), Length(max=200)],
    )
    ward = StringField('Ward', validators=[DataRequired(message='Ward is required.'), Length(max=150)])
    county = SelectField(
        'County',
        choices=[(c, c) for c in KENYA_COUNTIES],
        validators=[DataRequired()],
    )
    financial_year = StringField(
        'Financial Year',
        validators=[DataRequired(message='Financial year is required.'), Length(max=20)],
        render_kw={'placeholder': 'e.g. 2025/2026'},
    )
    allocated_budget = FloatField(
        'Allocated Budget (KES)',
        validators=[DataRequired(message='Allocated budget is required.'), NumberRange(min=0)],
    )
    amount_spent = FloatField(
        'Amount Spent (KES)',
        validators=[DataRequired(message='Amount spent is required.'), NumberRange(min=0)],
    )
    project_status = SelectField(
        'Project Status',
        choices=[(s, s) for s in PROJECT_STATUSES],
        validators=[DataRequired()],
    )
    submit = SubmitField('Save Project')

    def validate_amount_spent(self, field):
        if self.allocated_budget.data is not None and field.data is not None:
            if field.data > self.allocated_budget.data:
                raise ValidationError('Amount spent cannot exceed the allocated budget.')
