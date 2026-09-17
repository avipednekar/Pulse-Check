FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system pulsecheck && adduser --system --ingroup pulsecheck pulsecheck
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations
COPY docker ./docker
COPY wsgi.py .
RUN chmod +x /app/docker/entrypoint.sh && chown -R pulsecheck:pulsecheck /app

USER pulsecheck
EXPOSE 5000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
