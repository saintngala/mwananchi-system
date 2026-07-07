"""
SQLAlchemy models for the Mwananchi System.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Complaint(db.Model):
    """A community complaint submitted by a citizen."""

    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    citizen_name = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(30), default='Submitted', nullable=False)

    def __repr__(self):
        return f'<Complaint {self.report_id} ({self.status})>'


class Budget(db.Model):
    """A county development project tracked for budget transparency."""

    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    ward = db.Column(db.String(150), nullable=False)
    county = db.Column(db.String(100), nullable=False)
    financial_year = db.Column(db.String(20), nullable=False)
    allocated_budget = db.Column(db.Float, nullable=False, default=0)
    amount_spent = db.Column(db.Float, nullable=False, default=0)
    progress_percentage = db.Column(db.Float, nullable=False, default=0)
    project_status = db.Column(db.String(30), default='Not Started', nullable=False)

    def __repr__(self):
        return f'<Budget {self.project_name} ({self.county})>'


class Admin(UserMixin, db.Model):
    """An administrator account with access to the admin dashboard."""

    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))
