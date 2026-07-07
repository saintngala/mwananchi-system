"""
Seed the Mwananchi System database with sample data for development and demos.

Usage:
    python seed_data.py

Safe to re-run: it skips any table that already has data, so it will not
create duplicates.
"""
import random
from datetime import datetime, timedelta

from app import create_app, db
from app.models import Complaint, Budget, Admin
from app.utils import (
    COMPLAINT_CATEGORIES, COMPLAINT_STATUSES, calculate_progress,
)

app = create_app()

SAMPLE_LOCATIONS = [
    'Kibera, Nairobi', 'Kawangware, Nairobi', 'Mtwapa, Kilifi', 'Kondele, Kisumu',
    'Kaptembwo, Nakuru', 'Bomas, Uasin Gishu', 'Manyatta, Kisumu', 'Kayole, Nairobi',
    'Nyalenda, Kisumu', 'Shauri Moyo, Nairobi',
]

SAMPLE_DESCRIPTIONS = {
    'Water Supply': 'There has been no piped water in our estate for over two weeks.',
    'Electricity & Power': 'Frequent power blackouts are affecting local businesses.',
    'Roads & Infrastructure': 'The main access road has large potholes that damage vehicles.',
    'Sanitation & Waste Management': 'Garbage has not been collected from our area in three weeks.',
    'Health Services': 'The local health centre has run out of essential medicine.',
    'Security': 'Street lighting is broken, making the area unsafe at night.',
    'Education': 'The primary school lacks enough desks for all pupils.',
    'Corruption / Misconduct': 'Reports of bribery when accessing county services.',
    'Agriculture': 'Delayed distribution of subsidised farm inputs this season.',
    'Other': 'General feedback regarding county service delivery.',
}

SAMPLE_NAMES = [None, None, 'Jane W.', 'Otieno K.', 'Amina H.', 'Peter M.', None]
SAMPLE_PHONES = [None, None, '0712345678', '0798765432', '0722334455']

# (project_name, ward, county, financial_year, allocated_budget, amount_spent, project_status)
SAMPLE_PROJECTS = [
    ('Borehole Drilling Project', 'Kibra', 'Nairobi', '2025/2026', 8500000, 6200000, 'Ongoing'),
    ('Market Shed Construction', 'Kondele', 'Kisumu', '2025/2026', 4200000, 4200000, 'Completed'),
    ('Rural Electrification Phase II', 'Turbo', 'Uasin Gishu', '2025/2026', 15000000, 3000000, 'Delayed'),
    ('County Referral Hospital Wing', 'Nakuru East', 'Nakuru', '2024/2025', 62000000, 58000000, 'Ongoing'),
    ('Feeder Roads Upgrade', 'Mtwapa', 'Kilifi', '2025/2026', 21000000, 0, 'Not Started'),
    ('Youth Empowerment Centre', 'Kayole North', 'Nairobi', '2024/2025', 9800000, 9800000, 'Completed'),
    ('Storm Water Drainage', 'Shauri Moyo', 'Nairobi', '2025/2026', 5400000, 1200000, 'Stalled'),
    ('Early Childhood Education Classrooms', 'Manyatta', 'Kisumu', '2025/2026', 7300000, 4100000, 'Ongoing'),
    ('Livestock Sale Yard', 'Ainabkoi', 'Uasin Gishu', '2024/2025', 3600000, 3550000, 'Completed'),
    ('Solar Street Lighting', 'Bomas', 'Uasin Gishu', '2025/2026', 6100000, 2000000, 'Ongoing'),
]

DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_EMAIL = 'admin@mwananchi.go.ke'
DEFAULT_ADMIN_PASSWORD = 'Mwananchi@2026'


def seed():
    with app.app_context():
        db.create_all()

        # --- Default admin account --------------------------------------
        if not Admin.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first():
            admin = Admin(username=DEFAULT_ADMIN_USERNAME, email=DEFAULT_ADMIN_EMAIL)
            admin.set_password(DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin)
            print(f'Created default admin -> username: {DEFAULT_ADMIN_USERNAME} | password: {DEFAULT_ADMIN_PASSWORD}')
            print('IMPORTANT: change this password immediately after your first login.')
        else:
            print('Admin account already exists, skipping.')

        # --- Sample complaints ---------------------------------------------
        if Complaint.query.count() == 0:
            year = datetime.utcnow().year
            for i in range(20):
                category = random.choice(COMPLAINT_CATEGORIES)
                days_ago = random.randint(0, 60)
                complaint = Complaint(
                    report_id=f'MWN-{year}-{i + 1:06d}',
                    category=category,
                    description=SAMPLE_DESCRIPTIONS.get(category, 'Citizen reported issue.'),
                    location=random.choice(SAMPLE_LOCATIONS),
                    citizen_name=random.choice(SAMPLE_NAMES),
                    phone_number=random.choice(SAMPLE_PHONES),
                    date_submitted=datetime.utcnow() - timedelta(days=days_ago),
                    status=random.choice(COMPLAINT_STATUSES),
                )
                db.session.add(complaint)
            print('Created 20 sample complaints.')
        else:
            print('Complaints already exist, skipping sample complaints.')

        # --- Sample budget projects ------------------------------------------
        if Budget.query.count() == 0:
            for name, ward, county, fy, allocated, spent, status in SAMPLE_PROJECTS:
                project = Budget(
                    project_name=name,
                    ward=ward,
                    county=county,
                    financial_year=fy,
                    allocated_budget=allocated,
                    amount_spent=spent,
                    progress_percentage=calculate_progress(allocated, spent),
                    project_status=status,
                )
                db.session.add(project)
            print(f'Created {len(SAMPLE_PROJECTS)} sample budget projects.')
        else:
            print('Budget projects already exist, skipping sample projects.')

        db.session.commit()
        print('Database seeding complete.')


if __name__ == '__main__':
    seed()
