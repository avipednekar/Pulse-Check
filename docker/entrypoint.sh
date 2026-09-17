#!/bin/sh
set -eu

flask --app 'app:create_app' db upgrade
exec gunicorn --workers 1 --bind 0.0.0.0:5000 wsgi:app
