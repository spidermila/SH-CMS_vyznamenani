# syntax=docker/dockerfile:1

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements-web.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY libs /app/libs
COPY web /app/web

RUN chmod +x /app/web/healthcheck.sh

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD ["/app/web/healthcheck.sh"]

CMD ["gunicorn", "web.app:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "1", "--threads", "4", \
     "--log-level", "debug", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output"]
