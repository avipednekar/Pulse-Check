"""Web and JSON routes for PulseCheck."""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from .checker import all_statuses, run_check, status_for_url
from .extensions import db
from .models import CheckResult, MonitoredUrl

bp = Blueprint("main", __name__)


def normalize_url(value: str) -> str:
    """Validate and normalize an HTTP(S) URL suitable for requests."""
    raw_url = value.strip()
    try:
        parsed = urlsplit(raw_url)
        port = parsed.port  # evaluates malformed ports while still inside try
    except ValueError as exc:
        raise ValueError("Enter a valid HTTP or HTTPS URL.") from exc

    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Enter a complete HTTP or HTTPS URL.")
    if parsed.username or parsed.password:
        raise ValueError("URLs with embedded credentials are not allowed.")

    host = parsed.hostname.lower()
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    netloc = host if port is None else f"{host}:{port}"
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, ""))


@bp.get("/")
def dashboard():
    return render_template("dashboard.html", statuses=all_statuses())


@bp.get("/api/status")
def api_status():
    return jsonify(all_statuses())


@bp.get("/urls/<int:url_id>")
def url_history(url_id: int):
    """Show the complete persisted check history for one monitored URL."""
    monitored_url = db.get_or_404(MonitoredUrl, url_id)
    checks = monitored_url.checks.order_by(CheckResult.checked_at.desc()).all()
    return render_template(
        "url_history.html",
        monitored_url=monitored_url,
        status=status_for_url(monitored_url),
        checks=checks,
    )


@bp.get("/api/checks/<int:url_id>")
def api_checks(url_id: int):
    """Return check history as JSON, optionally filtered by date_from and date_to."""
    from datetime import datetime, timezone

    monitored_url = db.get_or_404(MonitoredUrl, url_id)
    query = monitored_url.checks

    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from).replace(tzinfo=timezone.utc)
            query = query.filter(CheckResult.checked_at >= dt_from)
        except ValueError:
            pass

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            query = query.filter(CheckResult.checked_at <= dt_to)
        except ValueError:
            pass

    checks = query.order_by(CheckResult.checked_at.desc()).all()
    return jsonify([
        {
            "checked_at": check.checked_at.isoformat(),
            "is_up": check.is_up,
            "status_code": check.status_code,
            "response_time_ms": check.response_time_ms,
            "error_message": check.error_message,
        }
        for check in checks
    ])


@bp.post("/add-url")
def add_url():
    try:
        normalized_url = normalize_url(request.form.get("url", ""))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("main.dashboard"))

    monitored_url = MonitoredUrl(url=normalized_url)
    db.session.add(monitored_url)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("That URL is already being monitored.", "warning")
    else:
        flash("URL added. Its first scheduled check will run within ten minutes.", "success")
    return redirect(url_for("main.dashboard"))


@bp.post("/api/check/<int:url_id>")
def check_now(url_id: int):
    monitored_url = db.get_or_404(MonitoredUrl, url_id)
    run_check(monitored_url)
    return jsonify(status_for_url(monitored_url))
