# Technology Stack

First-tier component selections:

- Backend framework: FastAPI
- Database: TimescaleDB (PostgreSQL extension)
- ORM & migrations: SQLAlchemy 2.x + Alembic
- Device communication: pymodbus (Modbus TCP/RTU only)
- Scheduling: APScheduler
- Authentication: JWT (HttpOnly cookies, SameSite=Strict) + Argon2
- API transport: REST endpoints + WebSockets (WebSockets primary for live data)
- Frontend: React + TypeScript + Vite
- UI library: Ant Design
- Charting: ECharts
- Client state management: TanStack Query + Zustand
- Internationalization: react-i18next
- Python package manager: uv
- Python linting & types: Ruff + mypy
- Python testing: pytest
- Frontend linting & formatting: ESLint + Prettier
- Frontend testing: Vitest
- CI/CD: GitHub Actions
- Containerization & proxy: Docker Compose + Nginx
- Configuration management: Pydantic Settings (.env)
