# DDMS Development Guide

## Quick Start

### Docker Development (Recommended)
```bash
# Start all services
docker compose up -d

# Access:
# - Backend: http://localhost:8001
# - API Docs: http://localhost:8001/api/docs
# - Frontend: http://localhost:8081
# - Database: localhost:5433
```

### Local Backend Development (Fastest)
```bash
# Start only database
docker compose up -d db

# Run backend locally (hot reload)
cd backend
source .venv/bin/activate
uvicorn ddms.main:app --reload --port 8001

# Access:
# - Backend: http://localhost:8001
# - API Docs: http://localhost:8001/api/docs
```

---

## Debugging Backend in Docker

### View Logs
```bash
# Follow backend logs
docker compose logs -f backend

# View last 100 lines
docker compose logs backend --tail 100
```

### Execute Commands Inside Container
```bash
# Get shell access
docker exec -it claude-backend sh

# Run health check directly
docker exec claude-backend curl http://localhost:8000/api/health

# Run pytest inside container
docker exec claude-backend pytest -v

# Check environment variables
docker exec claude-backend env | grep DDMS_
```

### Health Check Status
```bash
# Check if backend is healthy
docker compose ps backend

# Inspect health check details
docker inspect claude-backend --format='{{json .State.Health}}' | python3 -m json.tool
```

### Database Access
```bash
# Connect to database
docker exec -it claude-db psql -U ddms -d ddms

# Connect to database (dev mode with port exposed)
psql -h localhost -p 5433 -U ddms -d ddms

# Run SQL query directly
docker exec claude-db psql -U ddms -d ddms -c "SELECT version();"
```

---

## Testing

### Run Tests Locally
```bash
cd backend
source .venv/bin/activate

# All tests
pytest -v

# With coverage
pytest --cov=ddms --cov-report=term --cov-report=html

# Specific test file
pytest tests/unit/test_health.py -v

# Specific test
pytest tests/unit/test_health.py::test_system_health -v
```

### Run Tests in Docker
```bash
# Run tests inside backend container
docker exec claude-backend pytest -v

# With coverage
docker exec claude-backend pytest --cov=ddms --cov-report=term
```

---

## Code Quality

### Linting and Formatting
```bash
cd backend
source .venv/bin/activate

# Check linting
ruff check ddms tests

# Auto-fix linting issues
ruff check --fix ddms tests

# Check formatting
ruff format --check ddms tests

# Auto-format
ruff format ddms tests

# Type checking
mypy ddms
```

---

## API Testing

### Using curl
```bash
# Direct backend access
curl http://localhost:8001/api/health
curl http://localhost:8001/api/version

# Through Nginx proxy
curl http://localhost:8081/api/health

# Interactive API docs
open http://localhost:8001/api/docs
open http://localhost:8001/api/redoc

# OpenAPI schema
curl http://localhost:8001/api/openapi.json
```

### Using httpie
```bash
# Install: brew install httpie

# Pretty JSON output
http :8001/api/health
http :8001/api/version
```

---

## Database Operations

### Migrations
```bash
cd backend
source .venv/bin/activate

# Create new migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

### Reset Database
```bash
# Stop services
docker compose down

# Remove database volume
docker volume rm claude_db-data

# Restart services (will create fresh DB)
docker compose up -d
```

---

## Port Reference

### Docker Services
- **8001**: Backend (FastAPI) - direct access, hot reload enabled
- **8081**: Nginx (frontend + API proxy)
- **5433**: PostgreSQL - for database tools (pgAdmin, DBeaver, etc.)

**Note:** Ports chosen to avoid conflicts with codex project (8000, 8080, 5432)

### Local Development (no Docker)
- **8001**: Backend (uvicorn)
- **5433**: PostgreSQL (Docker)
- **3000**: Frontend dev server (npm run dev)

---

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker compose logs backend

# Rebuild image
docker compose build backend --no-cache
docker compose up -d backend

# Check dependencies
docker exec claude-backend pip list
```

### Database connection issues
```bash
# Check database is healthy
docker compose ps db

# Test connection from backend
docker exec claude-backend python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgresql://ddms:password@db:5432/ddms')
    print(await conn.fetchval('SELECT version()'))
    await conn.close()
asyncio.run(test())
"
```

### Port conflicts
```bash
# Check what's using port 8080
lsof -i :8080

# Check what's using port 8000
lsof -i :8000

# Kill process using port
kill -9 <PID>
```

---

## Best Practices

1. **Use Docker for standard development** - Consistent environment with hot reload
2. **Run backend locally for deep debugging** - Full IDE integration, breakpoints
3. **Always run tests before committing** - `pytest && ruff check && mypy`
4. **Check logs frequently** - `docker compose logs -f`
5. **Use docker exec for container inspection** - Direct access to running containers
