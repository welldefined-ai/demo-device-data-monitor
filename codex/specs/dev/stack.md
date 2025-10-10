# Stack Decisions

First-tier component selections (concise; no implementation details):

- Backend framework: FastAPI
- Database: PostgreSQL (consider TimescaleDB later if needed)
- ORM & migrations: SQLAlchemy 2.x + Alembic
- Authentication: JWT (HttpOnly cookies) + Argon2
- Realtime: WebSockets
- Frontend: React + TypeScript + Vite
- UI library: Ant Design
- Charting: ECharts
- Client data fetching/state: TanStack Query
- Internationalization: react-i18next
- Python package manager: uv
- Linting & types: Ruff + mypy
- Testing: pytest
- CI/CD: GitHub Actions
- Containerization: Docker Compose
- Configuration management: Pydantic Settings (.env)
