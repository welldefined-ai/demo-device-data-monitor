# Technology Stack

## Backend

- **FastAPI** - Async web framework with WebSocket support
- **TimescaleDB** - PostgreSQL extension for time-series data
- **SQLAlchemy 2.x** - ORM for database operations
- **Alembic** - Database migrations
- **pymodbus** - Modbus TCP/RTU communication
- **APScheduler** - Background task scheduling (device polling, data cleanup)
- **JWT** - Authentication tokens in HTTP-only cookies (SameSite=Strict)
- **Argon2** - Password hashing
- **Pydantic Settings** - Configuration management (.env files)
- **uv** - Package manager
- **Ruff** - Linting and formatting
- **mypy** - Static type checking
- **pytest** - Testing framework

## Frontend

- **React** + **TypeScript** - UI framework
- **Vite** - Build tool
- **Ant Design** - UI component library
- **Apache ECharts** - Charting and visualization
- **Zustand** - Client state management
- **TanStack Query** - Server state and caching
- **react-i18next** - Internationalization
- **ESLint** + **Prettier** - Code quality
- **Vitest** - Testing framework

## Deployment

- **Docker** + **Docker Compose** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **GitHub Actions** - CI/CD pipeline

## Communication

- **WebSockets** - Real-time data push (primary)
- **REST API** - Configuration and historical data queries
