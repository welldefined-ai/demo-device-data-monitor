# Architecture Specification

## Service Architecture

Three-tier Docker Compose stack (+ dev-only simulator):
- **Web (Nginx)**: Serves the built React SPA at `/` and proxies `/api/*` + `/ws/*`
- **Backend (FastAPI)**: REST + WebSocket API, surfaced at `/api/*`. Runs APScheduler
  to poll devices at configured sampling intervals.
- **Database (TimescaleDB)**: PostgreSQL w/ time-series extensions (TimescaleDB 2.x)
- **Simulator (dev-only)**: Modbus TCP server on port 1502 that increments a counter
  in holding register 0 for end-to-end verification.

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
 - Dev convenience: optional auto-seed of a demo device targeting the simulator
   when `DDMS_DEV_AUTOCONFIG=1` is set (docker-compose sets this by default).

### Production (future iteration)
- Backend and DB internal only
- Nginx is the only external entry point
- Backend runs under process manager (gunicorn + lifespan)
