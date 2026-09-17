from app.extensions import db
from app.models import CheckResult, MonitoredUrl


def test_url_history_shows_all_recorded_checks(client, app):
    with app.app_context():
        monitored_url = MonitoredUrl(url="https://example.com/")
        db.session.add(monitored_url)
        db.session.flush()
        db.session.add_all(
            [
                CheckResult(monitored_url=monitored_url, is_up=True, status_code=200, response_time_ms=12),
                CheckResult(
                    monitored_url=monitored_url,
                    is_up=False,
                    error_message="Connection timed out",
                    response_time_ms=10000,
                ),
            ]
        )
        db.session.commit()
        url_id = monitored_url.id

    response = client.get(f"/urls/{url_id}")
    assert response.status_code == 200
    assert b"Check history" in response.data
    assert b"HTTP 200" in response.data
    assert b"Connection timed out" in response.data
    assert f"/urls/{url_id}".encode() in client.get("/").data
