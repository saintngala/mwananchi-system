"""
Application configuration.

All values can be overridden with environment variables, which makes it easy
to move from local SQLite development to a production PostgreSQL deployment
without touching any code (see README.md).
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core ---------------------------------------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-this-secret-key')

    # --- Database -------------------------------------------------------
    # Defaults to a local SQLite file under /instance. To move to
    # PostgreSQL in production, set DATABASE_URL, e.g.:
    #   postgresql://user:password@host:5432/mwananchi
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'instance', 'mwananchi.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Forms / CSRF -----------------------------------------------------
    WTF_CSRF_ENABLED = True

    # --- Sessions / cookies ------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Only send cookies over HTTPS. Keep this False for local HTTP development,
    # set SESSION_COOKIE_SECURE=True in production once you're behind HTTPS.
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'

    # --- Pagination ---------------------------------------------------
    ITEMS_PER_PAGE = 10

    # --- Request limits ------------------------------------------------
    # Caps total incoming request size. Nothing in this app accepts file
    # uploads, so 1 MB is generous for form submissions and defends against
    # trivial large-payload denial-of-service attempts.
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
