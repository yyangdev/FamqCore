FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 botuser

COPY src/app/ .
RUN mkdir -p /app/database /app/logs \
    && chown -R botuser:botuser /app

VOLUME ["/app/database", "/app/logs"]
USER botuser

# A running Discord gateway has no HTTP port. This check verifies the process
# and the database volume without requiring extra runtime dependencies.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import os, sqlite3; p='/app/database/database.db'; c=sqlite3.connect(p); c.execute('SELECT 1'); c.close(); raise SystemExit(0 if os.path.exists('/proc/1/cmdline') else 1)"

CMD ["python", "main.py"]
