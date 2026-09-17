# PulseCheck

PulseCheck is a local Flask uptime monitor. It stores URLs and their check history
in PostgreSQL, checks them every five minutes, and shows current status plus a
rolling 24-hour uptime percentage.

## Run with Docker

1. Copy `.env.example` to `.env` and replace both placeholder values with local secrets.
2. Start Docker Desktop.
3. Run `docker compose up --build`.
4. Open `http://localhost:5000`, add an HTTP/HTTPS URL, then use **Check now**
   for its first immediate result.

The application container applies the committed database migration before it starts.
PostgreSQL data is kept in the named `postgres_data` Docker volume.

The default scheduled interval is five minutes. To test locally, set
`CHECK_INTERVAL_MINUTES=1` in `.env`, then recreate the app with
`docker compose up -d --force-recreate app`.

## Local test run

Create a virtual environment, install dependencies, then run:

```powershell
python -m pytest -q
```

The test suite uses a temporary SQLite database and never starts the scheduler.

## Security note

This is an unauthenticated local-demo application. Do not expose it publicly
without adding authentication, CSRF protection, and stricter outbound URL rules.
