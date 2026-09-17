"""PulseCheck application factory."""

from __future__ import annotations

import os

from flask import Flask

from .extensions import db, migrate


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the PulseCheck Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///pulsecheck.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CHECK_TIMEOUT_SECONDS=float(os.getenv("CHECK_TIMEOUT_SECONDS", "10")),
        CHECK_INTERVAL_MINUTES=int(os.getenv("CHECK_INTERVAL_MINUTES", "5")),
        ENABLE_SCHEDULER=_env_flag("ENABLE_SCHEDULER", False),
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401 - registers SQLAlchemy models
    from .routes import bp

    app.register_blueprint(bp)

    if app.config["ENABLE_SCHEDULER"] and not app.config.get("TESTING"):
        from .scheduler import start_scheduler

        start_scheduler(app)

    return app
