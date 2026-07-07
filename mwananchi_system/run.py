"""
Entry point for running the Mwananchi System with Flask's development server.

For local development:
    python run.py

For production, do NOT use this file — use a proper WSGI server instead, e.g.:
    gunicorn "run:app" --bind 0.0.0.0:8000 --workers 4
See README.md for full deployment notes.
"""
import os

from dotenv import load_dotenv

# Load variables from a local .env file (if present) before the app config
# is built, so SECRET_KEY / DATABASE_URL / etc. can be overridden without
# editing any code. See .env.example.
load_dotenv()

from app import create_app, db
from app.models import Admin, Complaint, Budget

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Makes `flask shell` start with these already imported."""
    return {'db': db, 'Admin': Admin, 'Complaint': Complaint, 'Budget': Budget}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Fail safe: debug mode (which exposes Werkzeug's interactive, code-executing
    # debugger on unhandled errors) is OFF unless FLASK_DEBUG=True is explicitly
    # set, e.g. in a local .env file. Never rely on this being True in production.
    debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug, host='0.0.0.0', port=port)
