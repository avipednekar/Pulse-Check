"""Production entry point. Compose runs this with exactly one Gunicorn worker."""

from app import create_app

app = create_app({"ENABLE_SCHEDULER": True})
