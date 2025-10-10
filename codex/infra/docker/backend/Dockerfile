FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python deps (binary wheels preferred)
RUN pip install --no-cache-dir \
    fastapi uvicorn[standard] sqlalchemy alembic pydantic pydantic-settings psycopg[binary] \
    pymodbus apscheduler argon2-cffi python-jose[cryptography]

# Copy app
COPY backend /app

EXPOSE 8000
CMD ["uvicorn", "ddms.main:app", "--host", "0.0.0.0", "--port", "8000"]
