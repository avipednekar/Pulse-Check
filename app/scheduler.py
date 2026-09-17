"""Single-process scheduler setup for the Dockerized MVP."""

from apscheduler.schedulers.background import BackgroundScheduler

from .checker import run_all_checks


def start_scheduler(app) -> BackgroundScheduler:
    """Start one five-minute scheduler and retain it on the Flask app."""
    existing = app.extensions.get("pulsecheck_scheduler")
    if existing:
        return existing

    scheduler = BackgroundScheduler(timezone="UTC", daemon=True)
    scheduler.add_job(
        run_all_checks,
        trigger="interval",
        minutes=app.config["CHECK_INTERVAL_MINUTES"],
        args=[app],
        id="check_all_urls",
        replace_existing=True,
    )
    scheduler.start()
    app.extensions["pulsecheck_scheduler"] = scheduler
    return scheduler
