"""Web and JSON routes for PulseCheck."""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from .checker import all_statuses, run_check, status_for_url
from .extensions import db
from .models import MonitoredUrl

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
        flash("URL added. Its first scheduled check will run within five minutes.", "success")
    return redirect(url_for("main.dashboard"))


@bp.post("/api/check/<int:url_id>")
def check_now(url_id: int):
    monitored_url = db.get_or_404(MonitoredUrl, url_id)
    run_check(monitored_url)
    return jsonify(status_for_url(monitored_url))
