"""HTTP health-check execution and dashboard status calculations."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import requests
from flask import current_app

from .extensions import db
from .models import CheckResult, MonitoredUrl

USER_AGENT = "PulseCheck/1.0 (+local uptime monitor)"


def run_check(monitored_url: MonitoredUrl) -> CheckResult:
    """Check one URL and persist both successful and failed attempts."""
    status_code = None
    response_time_ms = None
    error_message = None
    is_up = False
    started_at = time.perf_counter()

    try:
        response = requests.get(
            monitored_url.url,
            timeout=current_app.config["CHECK_TIMEOUT_SECONDS"],
            headers={"User-Agent": USER_AGENT},
        )
        status_code = response.status_code
        response_time_ms = round((time.perf_counter() - started_at) * 1000)
        is_up = 200 <= status_code < 400
    except requests.RequestException as exc:
        response_time_ms = round((time.perf_counter() - started_at) * 1000)
        error_message = str(exc)[:500]

    result = CheckResult(
        monitored_url=monitored_url,
        status_code=status_code,
        response_time_ms=response_time_ms,
        is_up=is_up,
        error_message=error_message,
    )
    db.session.add(result)
    db.session.commit()
    return result


def run_all_checks(app) -> None:
    """Run scheduled checks inside an application context."""
    with app.app_context():
        urls = db.session.scalars(db.select(MonitoredUrl).order_by(MonitoredUrl.id)).all()
        for monitored_url in urls:
            run_check(monitored_url)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def status_for_url(monitored_url: MonitoredUrl, now: datetime | None = None) -> dict:
    """Return the latest state and rolling 24-hour uptime for one URL."""
    now = now or datetime.now(timezone.utc)
    window_start = now - timedelta(hours=24)
    latest = monitored_url.checks.order_by(CheckResult.checked_at.desc()).first()
    recent_checks = monitored_url.checks.filter(CheckResult.checked_at >= window_start).all()
    uptime_percent = None
    if recent_checks:
        uptime_percent = round(100 * sum(check.is_up for check in recent_checks) / len(recent_checks), 1)

    return {
        "id": monitored_url.id,
        "url": monitored_url.url,
        "state": "unknown" if latest is None else ("up" if latest.is_up else "down"),
        "status_code": latest.status_code if latest else None,
        "response_time_ms": latest.response_time_ms if latest else None,
        "error_message": latest.error_message if latest else None,
        "last_checked_at": _as_utc(latest.checked_at).isoformat() if latest else None,
        "uptime_percent": uptime_percent,
    }


def all_statuses() -> list[dict]:
    urls = db.session.scalars(db.select(MonitoredUrl).order_by(MonitoredUrl.created_at)).all()
    return [status_for_url(monitored_url) for monitored_url in urls]
