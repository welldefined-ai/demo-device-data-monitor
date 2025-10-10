# Development Setup

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop
- Git

## Initial Setup

### Option 1: Docker (Recommended)

```bash
docker compose up --build
```

Access:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: localhost:5433 (external), db:5432 (internal)

### Option 2: Local Development

**Backend:**
```bash
cd backend
pip install uv
uv pip install -e ".[dev]"
uvicorn ddms.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Port Configuration

- **Frontend**: 80 (Docker), 3000 (dev)
- **Backend**: 8000
- **Database**: 5433 (host) → 5432 (container)
  - Changed from default 5432 to avoid conflicts with local PostgreSQL

## Database Access

**From host machine:**
```bash
# Using psql
psql -h localhost -p 5433 -U ddms -d ddms

# Using Docker
docker compose exec db psql -U ddms -d ddms
```

**Connection details:**
- Host: localhost
- Port: 5433
- Database: ddms
- User: ddms
- Password: password

## Key Configuration Files

### Backend
- `backend/pyproject.toml` - Python dependencies and project metadata
- `backend/.env.example` - Environment variables template
- `backend/alembic.ini` - Database migration configuration

### Frontend
- `frontend/package.json` - Node dependencies
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/vite.config.ts` - Build and dev server configuration
- `frontend/.eslintrc.json` - Linting rules
- `frontend/.prettierrc` - Code formatting rules

### Infrastructure
- `docker-compose.yml` - Multi-container orchestration
- `infra/docker/backend/Dockerfile` - Backend container build
- `infra/docker/frontend/Dockerfile` - Frontend container build (multi-stage)
- `infra/nginx/conf/nginx.conf` - Reverse proxy configuration

## Verification

After starting the services, verify the setup:

1. **Frontend**: Visit http://localhost - should show green status indicators
2. **Backend API**: `curl http://localhost:8000/api/health`
3. **API Docs**: Visit http://localhost:8000/docs
4. **Database**: `docker compose exec db psql -U ddms -d ddms -c "SELECT version();"`

## Common Issues

### Port Conflicts
- Database port 5432 → Changed to 5433
- If port 80 is in use, modify docker-compose.yml frontend ports

### Docker Build Failures
- Backend requires `README.md` in backend directory
- Frontend uses `npm install` (not `npm ci`) for initial setup

### CORS Issues
- Backend CORS configured for http://localhost and http://localhost:3000
- Vite proxy configured for /api and /ws endpoints

## Development Workflow

1. Make changes to code
2. Backend auto-reloads (uvicorn --reload)
3. Frontend hot-reloads (Vite HMR)
4. Containers mount local directories for live updates

## Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test

# CI build (full)
./scripts/ci/build.sh
```

## Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Useful Commands

```bash
# View logs
docker compose logs -f

# Rebuild containers
docker compose up --build

# Stop services
docker compose down

# Reset database
docker compose down -v
./scripts/db/reset.sh

# Clean Docker cache
docker system prune -a
```
