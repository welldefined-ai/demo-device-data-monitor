# Project Directory Structure

```
claude/
├── backend/
│   ├── ddms/
│   │   ├── api/              # FastAPI routes and dependencies
│   │   ├── core/             # Configuration, security, logging
│   │   ├── db/               # SQLAlchemy models and repositories
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic layer
│   │   ├── ingestion/        # Modbus polling and device I/O
│   │   ├── scheduler/        # APScheduler jobs (polling, cleanup)
│   │   └── realtime/         # WebSocket handlers for data push
│   ├── alembic/
│   │   └── versions/         # Database migration files
│   └── tests/
│       ├── unit/             # Unit tests
│       └── integration/      # Integration tests
│
├── frontend/
│   ├── src/
│   │   ├── app/              # Application setup and routing
│   │   ├── features/         # Feature-based modules (devices, groups, etc.)
│   │   ├── components/       # Reusable UI components
│   │   ├── i18n/             # Internationalization resources
│   │   ├── lib/              # API and WebSocket clients
│   │   ├── store/            # State management (Zustand, TanStack Query)
│   │   └── utils/            # Shared utilities (formatters, validators, constants)
│   ├── public/               # Static assets
│   └── tests/
│       ├── unit/             # Component unit tests
│       └── e2e/              # End-to-end tests
│
├── infra/
│   ├── docker/
│   │   ├── backend/          # Backend Dockerfile and configs
│   │   └── frontend/         # Frontend Dockerfile and configs
│   ├── db/
│   │   └── init/             # TimescaleDB initialization and retention policies
│   └── nginx/
│       └── conf/             # Reverse proxy configurations
│
├── .github/
│   └── workflows/            # CI/CD pipeline definitions
│
├── docs/
│   └── api/                  # API documentation
│
├── specs/
│   ├── dev/                  # Development specifications
│   └── user/                 # User requirements
│
└── scripts/
    ├── dev/                  # Development helper scripts
    ├── ci/                   # CI/CD scripts
    └── db/                   # Database utility scripts
```
