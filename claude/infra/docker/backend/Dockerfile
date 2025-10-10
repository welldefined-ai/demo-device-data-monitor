FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY backend/pyproject.toml .
COPY backend/README.md .
COPY backend/ddms ./ddms
COPY backend/alembic ./alembic
COPY backend/alembic.ini .

# Install dependencies
RUN uv pip install --system -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "ddms.main:app", "--host", "0.0.0.0", "--port", "8000"]
