# Mwananchi System

A citizen engagement platform for Kenyan counties. Citizens can submit
community complaints and receive a trackable Report ID, follow the status
of a complaint over time, and review county budget and development project
information. County administrators get a dashboard to manage complaints and
maintain budget records.

Built with Python, Flask, and SQLAlchemy, using a Bootstrap 5 front end with
a custom government-inspired navy / green / gold theme and full dark mode
support.

---

## Features

- **Submit Complaint** — category, description, location, optional name and
  Kenyan phone number, with a unique `MWN-YYYY-NNNNNN` Report ID generated on
  submission.
- **Track Complaint** — look up a complaint by Report ID and see a visual
  progress tracker (Submitted → Under Review → In Progress → Resolved).
- **Budget Information** — searchable, sortable, paginated table of county
  development projects with progress bars, plus a printable report.
- **Admin Dashboard** — login-protected area to view stats and a status
  breakdown chart, manage complaints (view / update status / delete / export
  to CSV), and manage budget projects (add / edit / delete).
- **Security** — CSRF protection on every form, hashed passwords, SQLAlchemy
  ORM (no raw SQL) to prevent SQL injection, Jinja2 auto-escaping to prevent
  XSS, and configurable secure session cookies.
- **Polish** — dark mode toggle (remembered across visits), animated stat
  counters, loading states on form submission, printable complaint receipts
  and budget reports.

---

## Tech stack

| Layer      | Technology                                                   |
|------------|---------------------------------------------------------------|
| Backend    | Python 3, Flask, SQLAlchemy (via Flask-SQLAlchemy)            |
| Forms      | Flask-WTF / WTForms (CSRF + validation)                       |
| Auth       | Flask-Login, Werkzeug password hashing                        |
| Migrations | Flask-Migrate (Alembic)                                       |
| Database   | SQLite locally, PostgreSQL-ready for production               |
| Frontend   | Bootstrap 5, Font Awesome 6, Chart.js, vanilla JavaScript      |

---

## Project structure

```
mwananchi_system/
├── app/
│   ├── __init__.py          # Application factory, extension setup, CLI commands
│   ├── models.py             # Complaint, Budget, Admin SQLAlchemy models
│   ├── routes.py             # main_bp (public) and admin_bp (dashboard) blueprints
│   ├── forms.py              # Flask-WTF forms + validation
│   ├── utils.py              # Shared constants, report ID generator, progress calc
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── submit_complaint.html
│   │   ├── complaint_success.html
│   │   ├── complaint_receipt.html
│   │   ├── track_complaint.html
│   │   ├── budget.html
│   │   ├── budget_print.html
│   │   ├── 404.html
│   │   ├── 500.html
│   │   └── admin/
│   │       ├── base_admin.html
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── complaints.html
│   │       ├── budget_list.html
│   │       └── budget_form.html
│   └── static/
│       ├── css/style.css
│       ├── js/script.js
│       └── images/
├── migrations/                # Created by `flask db init` (see below)
├── instance/                  # Local SQLite database lives here (git-ignored)
├── config.py                  # Environment-driven configuration
├── run.py                     # Development entry point
├── seed_data.py               # Sample data + default admin account
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Getting started

### 1. Clone/extract the project and create a virtual environment

```bash
cd mwananchi_system
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# then edit .env and set a real SECRET_KEY
```

Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Set up the database

You have two options:

**Option A — quick start (recommended for trying the app out):**

```bash
python seed_data.py
```

This creates all tables, a default admin account, and sample complaints and
budget projects (see credentials below).

**Option B — formal migrations (recommended once you're customising models):**

```bash
flask db init        # only once, creates the migrations/ folder
flask db migrate -m "Initial migration"
flask db upgrade
flask create-admin   # interactive prompt for username/email/password
```

`flask create-admin` is a custom CLI command (defined in `app/__init__.py`)
that securely creates an admin account without needing to run any script.

### 5. Run the app

```bash
python run.py
```

Visit `http://127.0.0.1:5000`.

### Default admin login (from `seed_data.py`)

```
Username: admin
Password: Mwananchi@2026
```

**Change this password immediately** — either add a new admin with
`flask create-admin` and delete the seeded one, or update the password
directly via `flask shell`:

```python
from app import db
from app.models import Admin
a = Admin.query.filter_by(username='admin').first()
a.set_password('a-much-better-password')
db.session.commit()
```

---

## Moving to PostgreSQL

The app reads its database URL from the `DATABASE_URL` environment variable
and falls back to local SQLite if it isn't set. To use PostgreSQL:

1. `pip install psycopg2-binary`
2. In `.env`, set:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/mwananchi
   ```
3. Run `flask db upgrade` (or `python seed_data.py`) against the new database.

No application code needs to change.

---

## Deployment notes

This project ships with Flask's built-in development server (`run.py`),
which is **not** suitable for production. Before deploying:

- Run behind a real WSGI server, e.g. `gunicorn "run:app" --bind 0.0.0.0:8000 --workers 4`,
  fronted by Nginx or another reverse proxy.
- Set a strong, unique `SECRET_KEY` via environment variable — never commit it.
- Set `SESSION_COOKIE_SECURE=True` once you're serving over HTTPS.
- Set `FLASK_DEBUG=False` (the default in production; `run.py` only enables
  debug mode when `FLASK_DEBUG=True` is explicitly set).
- Point `DATABASE_URL` at PostgreSQL rather than SQLite for concurrent access.
- Review `generate_report_id()` in `app/utils.py` if you expect a high volume
  of simultaneous submissions — the current approach (look up the highest
  existing sequence number and increment) is simple and fine for typical
  traffic, but a very high-concurrency deployment should add a database-level
  sequence or row lock to fully rule out a race condition.

---

## Validation & security summary

- **CSRF protection** — enabled globally via `Flask-WTF`'s `CSRFProtect`;
  every POST form includes a CSRF token (including plain HTML delete-buttons,
  which carry a manually-included hidden `csrf_token` field).
- **Password hashing** — `werkzeug.security.generate_password_hash` /
  `check_password_hash`, never plain text.
- **SQL injection protection** — all queries go through the SQLAlchemy ORM.
- **XSS protection** — Jinja2 auto-escaping is on by default; no user input
  is ever rendered with the `|safe` filter.
- **Open-redirect protection** — the admin login's `?next=` parameter is
  validated by `is_safe_redirect_url()` (`app/utils.py`) before it's ever
  redirected to, so a crafted `/admin/login?next=https://evil.example` link
  can't send an authenticating admin off-site.
- **Debug mode is off by default** — `run.py` only enables Werkzeug's
  interactive debugger when `FLASK_DEBUG=True` is explicitly set (e.g. in a
  local `.env`). If no environment is configured at all, the safe default
  applies.
- **Request size cap** — `MAX_CONTENT_LENGTH` (1 MB) in `config.py` rejects
  oversized request bodies outright; nothing in this app needs file uploads.
- **Phone validation** — Kenyan mobile numbers (Safaricom/Airtel/Telkom
  prefixes) via a regex validator, e.g. `0712345678`, `+254712345678`.
- **Clear error messages** — empty required fields, invalid phone numbers,
  unknown Report IDs ("No complaint found."), and invalid login credentials
  all surface specific, human-readable messages.

### Suggested further hardening (not included, since they pull in extra
dependencies beyond what was asked for, but worth adding before a public launch)

- **Rate limiting on `/admin/login`** — e.g. `Flask-Limiter`, to slow down
  brute-force password guessing. Nothing in the current build throttles
  repeated login attempts.
- **Security headers / CSP** — e.g. `flask-talisman`, to add HSTS, a
  Content-Security-Policy, and `X-Frame-Options` automatically. The app's own
  templates and `script.js` contain no inline event-handler attributes
  (delete confirmations use a `data-confirm` attribute handled by a single
  delegated listener, not `onsubmit="..."`), so it's already compatible with
  a `script-src` policy that omits `'unsafe-inline'`.
- **Account lockout / login throttling** after repeated failed attempts.

---

## License

This project was generated as a starting point for your own Mwananchi System
deployment — adapt it freely for your county or organisation.
