"""
Application factory for the Mwananchi System.

Using the factory pattern (create_app) rather than a single global app
object keeps imports clean, avoids circular-import problems between
models/routes, and makes the app easy to configure differently for
testing vs. production.
"""
from datetime import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

from config import Config

# Extensions are created here (unbound) and attached to the app inside
# create_app(). This is the standard pattern that avoids circular imports:
# models.py can safely do `from app import db` because `db` already exists
# as soon as the `app` package starts importing, well before create_app()
# actually runs.
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Initialize extensions ------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin dashboard.'
    login_manager.login_message_category = 'info'

    # --- Register blueprints ------------------------------------------
    from app.routes import main_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # --- Make sure models are registered with SQLAlchemy -----------------
    from app import models  # noqa: F401

    # --- Template globals -------------------------------------------------
    @app.context_processor
    def inject_globals():
        return {'current_year': datetime.utcnow().year}

    @app.template_filter('status_slug')
    def status_slug(value):
        """Turn a status string like 'Under Review' into 'under-review' for
        use as a CSS class suffix (e.g. status-under-review). Centralising
        this here means the same slugification rule is used everywhere a
        status badge is rendered, instead of repeating `|lower|replace`
        across every template that shows one."""
        return value.lower().replace(' ', '-') if value else ''

    # --- Error handlers -------------------------------------------------
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # --- CLI commands -------------------------------------------------
    register_cli_commands(app)

    return app


def register_cli_commands(app):
    import click

    @app.cli.command('create-admin')
    @click.option('--username', prompt=True, help='Username for the new admin account.')
    @click.option('--email', prompt=True, help='Email address for the new admin account.')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
                  help='Password for the new admin account.')
    def create_admin(username, email, password):
        """Create a new admin user from the command line."""
        from app.models import Admin

        if Admin.query.filter_by(username=username).first():
            click.echo(f'An admin with the username "{username}" already exists.')
            return

        admin = Admin(username=username, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Admin account "{username}" created successfully.')
