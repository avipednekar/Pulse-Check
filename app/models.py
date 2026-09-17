"""Database models for monitored URLs and their check history."""

from __future__ import annotations

from datetime import datetime, timezone

from .extensions import db


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MonitoredUrl(db.Model):
    __tablename__ = "monitored_urls"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    checks = db.relationship(
        "CheckResult",
        back_populates="monitored_url",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )


class CheckResult(db.Model):
    __tablename__ = "check_results"
    __table_args__ = (
        db.Index("ix_check_results_url_checked_at", "monitored_url_id", "checked_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    monitored_url_id = db.Column(
        db.Integer, db.ForeignKey("monitored_urls.id", ondelete="CASCADE"), nullable=False
    )
    checked_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    status_code = db.Column(db.Integer, nullable=True)
    response_time_ms = db.Column(db.Integer, nullable=True)
    is_up = db.Column(db.Boolean, nullable=False)
    error_message = db.Column(db.String(500), nullable=True)
    monitored_url = db.relationship("MonitoredUrl", back_populates="checks")
