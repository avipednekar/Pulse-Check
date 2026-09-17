from unittest.mock import patch

from app.extensions import db
from app.models import CheckResult, MonitoredUrl


def test_dashboard_renders_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Add a URL to begin monitoring" in response.data


def test_add_url_normalizes_and_redirects(client, app):
    response = client.post("/add-url", data={"url": " HTTPS://Example.COM/health#ignored "})
    assert response.status_code == 302
    with app.app_context():
        monitored_url = db.session.scalar(db.select(MonitoredUrl))
        assert monitored_url.url == "https://example.com/health"


def test_add_url_rejects_invalid_and_duplicate_urls(client, app):
    invalid = client.post("/add-url", data={"url": "ftp://example.com"}, follow_redirects=True)
    assert b"complete HTTP or HTTPS" in invalid.data

    client.post("/add-url", data={"url": "https://example.com"})
    duplicate = client.post("/add-url", data={"url": "https://example.com/"}, follow_redirects=True)
    assert b"already being monitored" in duplicate.data
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(MonitoredUrl.id))) == 1


def test_status_api_returns_dashboard_shape(client, app):
    with app.app_context():
        monitored_url = MonitoredUrl(url="https://example.com/")
        db.session.add(monitored_url)
        db.session.add(CheckResult(monitored_url=monitored_url, is_up=True, status_code=200, response_time_ms=12))
        db.session.commit()

    response = client.get("/api/status")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload[0]["url"] == "https://example.com/"
    assert payload[0]["state"] == "up"
    assert payload[0]["uptime_percent"] == 100.0


def test_manual_check_returns_updated_status(client, app):
    with app.app_context():
        monitored_url = MonitoredUrl(url="https://example.com/")
        db.session.add(monitored_url)
        db.session.commit()
        url_id = monitored_url.id

    with patch("app.routes.run_check") as run_check:
        response = client.post(f"/api/check/{url_id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == url_id
    run_check.assert_called_once()
