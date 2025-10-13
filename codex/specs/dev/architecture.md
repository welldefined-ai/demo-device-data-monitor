# Architecture Specification

## Service Architecture

Three-tier Docker Compose stack:
- **Web (Nginx)**: Serves the built React SPA at `/` and proxies `/api/*` + `/ws/*`
- **Backend (FastAPI)**: REST + WebSocket API, surfaced at `/api/*`
- **Database (TimescaleDB)**: PostgreSQL w/ time-series extensions (TimescaleDB 2.x)

## API Design

### Endpoint Structure
- **All endpoints under `/api/` prefix**
- Examples: `/api/health`, `/api/version`, `/api/docs`
- Rationale: Keeps browser routes (React) separate from API routes

## Configuration

### Environment Variables
- **Prefix: `DDMS_*`**
- Example: `DDMS_ENV`, `DDMS_DATABASE_URL`

## Deployment Modes

### Development
- Backend exposed for direct access and debugging
- Hot reload enabled via volume mounts
- Database exposed for local tools (pgAdmin, DBeaver)

### Production (future iteration)
- Backend and DB internal only
- Nginx is the only external entry point
- Backend runs under process manager (gunicorn + lifespan)
