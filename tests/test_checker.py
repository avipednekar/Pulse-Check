from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
import requests

from app.checker import run_check, status_for_url
from app.extensions import db
from app.models import CheckResult, MonitoredUrl


def add_url(url="https://example.com"):
    monitored_url = MonitoredUrl(url=url)
    db.session.add(monitored_url)
    db.session.commit()
    return monitored_url


@pytest.mark.parametrize("status_code,is_up", [(200, True), (302, True), (404, False), (500, False)])
def test_run_check_records_http_result(app, status_code, is_up):
    with app.app_context(), patch("app.checker.requests.get") as get:
        get.return_value = Mock(status_code=status_code)
        monitored_url = add_url()
        result = run_check(monitored_url)

        assert result.status_code == status_code
        assert result.is_up is is_up
        assert result.error_message is None
        assert result.response_time_ms is not None
        assert db.session.scalar(db.select(db.func.count(CheckResult.id))) == 1


@pytest.mark.parametrize("error", [requests.Timeout("timed out"), requests.ConnectionError("name not known")])
def test_run_check_records_request_errors(app, error):
    with app.app_context(), patch("app.checker.requests.get", side_effect=error):
        result = run_check(add_url())

        assert result.is_up is False
        assert result.status_code is None
        assert "".join(result.error_message).lower() in {"timed out", "name not known"}
        assert result.response_time_ms is not None


def test_status_uses_rolling_24_hour_uptime(app):
    with app.app_context():
        monitored_url = add_url()
        now = datetime.now(timezone.utc)
        db.session.add_all(
            [
                CheckResult(monitored_url=monitored_url, checked_at=now - timedelta(hours=1), is_up=True, status_code=200),
                CheckResult(monitored_url=monitored_url, checked_at=now - timedelta(hours=2), is_up=False, status_code=500),
                CheckResult(monitored_url=monitored_url, checked_at=now - timedelta(hours=25), is_up=True, status_code=200),
            ]
        )
        db.session.commit()

        status = status_for_url(monitored_url, now=now)
        assert status["uptime_percent"] == 50.0
        assert status["state"] == "up"


def test_status_is_unknown_without_history(app):
    with app.app_context():
        status = status_for_url(add_url())
        assert status["state"] == "unknown"
        assert status["uptime_percent"] is None
