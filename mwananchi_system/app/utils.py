"""
Shared constants and helper functions used across forms, models, and routes.
Centralising choice-lists here means the dropdown options shown to a citizen,
the values stored in the database, and the values validated on submission
always stay in sync.
"""
from datetime import datetime
from urllib.parse import urlparse, urljoin

from flask import request

# Categories a citizen can select when submitting a complaint.
COMPLAINT_CATEGORIES = [
    'Water Supply',
    'Electricity & Power',
    'Roads & Infrastructure',
    'Sanitation & Waste Management',
    'Health Services',
    'Security',
    'Education',
    'Corruption / Misconduct',
    'Agriculture',
    'Other',
]

# Lifecycle a complaint moves through. Order matters here: it drives the
# progress tracker shown on the "Track Complaint" page.
COMPLAINT_STATUSES = [
    'Submitted',
    'Under Review',
    'In Progress',
    'Resolved',
    'Rejected',
]

# Status values for county development/budget projects.
PROJECT_STATUSES = [
    'Not Started',
    'Ongoing',
    'Completed',
    'Delayed',
    'Stalled',
]

# Kenya's 47 counties, used to populate the budget project county dropdown.
KENYA_COUNTIES = [
    'Mombasa', 'Kwale', 'Kilifi', 'Tana River', 'Lamu', 'Taita-Taveta',
    'Garissa', 'Wajir', 'Mandera', 'Marsabit', 'Isiolo', 'Meru',
    'Tharaka-Nithi', 'Embu', 'Kitui', 'Machakos', 'Makueni', 'Nyandarua',
    'Nyeri', 'Kirinyaga', "Murang'a", 'Kiambu', 'Turkana', 'West Pokot',
    'Samburu', 'Trans Nzoia', 'Uasin Gishu', 'Elgeyo-Marakwet', 'Nandi',
    'Baringo', 'Laikipia', 'Nakuru', 'Narok', 'Kajiado', 'Kericho',
    'Bomet', 'Kakamega', 'Vihiga', 'Bungoma', 'Busia', 'Siaya',
    'Kisumu', 'Homa Bay', 'Migori', 'Kisii', 'Nyamira', 'Nairobi',
]

# Matches phone numbers like 0712345678, 254712345678, +254712345678,
# 0112345678 (covers Safaricom/Airtel/Telkom mobile prefixes 7xx and 1xx).
KENYAN_PHONE_REGEX = r'^(?:\+254|254|0)(7|1)\d{8}$'

REPORT_ID_PREFIX = 'MWN'


def generate_report_id():
    """
    Generate a unique, sequential report ID in the form MWN-YYYY-NNNNNN.
    Numbering restarts at 000001 at the start of each calendar year.

    Note: this looks up the highest existing sequence number for the
    current year and increments it. That is simple and fine for a
    single-process app; a high-concurrency production deployment should
    guard this with a database-level sequence or a row lock to fully
    rule out a race between two simultaneous submissions.
    """
    from app.models import Complaint  # local import avoids a circular import

    year = datetime.utcnow().year
    prefix = f'{REPORT_ID_PREFIX}-{year}-'

    last_complaint = (
        Complaint.query.filter(Complaint.report_id.like(f'{prefix}%'))
        .order_by(Complaint.id.desc())
        .first()
    )

    if last_complaint:
        last_seq = int(last_complaint.report_id.split('-')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f'{prefix}{new_seq:06d}'


def calculate_progress(allocated_budget, amount_spent):
    """Safely calculate the percentage of a budget project's funds spent."""
    if not allocated_budget or allocated_budget <= 0:
        return 0.0
    percentage = (amount_spent / allocated_budget) * 100
    return round(max(0.0, min(percentage, 100.0)), 2)


def is_safe_redirect_url(target):
    """
    Return True only if `target` is a relative URL on this same site.

    Used to validate the ?next= parameter after a successful admin login
    before redirecting to it. Without this check, a crafted link like
    /admin/login?next=https://evil.example/phish would send an admin who
    clicks it straight to an external site immediately after they
    authenticate — a classic open-redirect vulnerability that's easy to
    weaponise for phishing. Any absolute URL pointing at a different host
    (or a different scheme) is rejected.
    """
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
