# DDMS - Distributed Device Monitoring System

A distributed monitoring system for industrial devices using Modbus protocol with real-time data visualization.

## Project Structure

```
claude/
├── backend/          # FastAPI backend application
├── frontend/         # React + TypeScript frontend
├── infra/           # Infrastructure and deployment configs
├── docs/            # Documentation
├── specs/           # Project specifications
└── scripts/         # Utility scripts
```

## Technology Stack

### Backend
- FastAPI (async web framework)
- TimescaleDB (time-series database)
- SQLAlchemy 2.x (ORM)
- Alembic (migrations)
- pymodbus (Modbus communication)

### Frontend
- React + TypeScript
- Vite (build tool)
- Ant Design (UI components)
- Apache ECharts (charts)
- Zustand (state management)

### Infrastructure
- Docker + Docker Compose
- Nginx (reverse proxy)
- GitHub Actions (CI/CD)

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker and Docker Compose

### Quick Start

1. Clone the repository
2. Run setup script:
   ```bash
   ./scripts/dev/setup.sh
   ```

3. Start with Docker:
   ```bash
   docker compose up
   ```

4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development

**Backend:**
```bash
cd backend
uvicorn ddms.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Documentation

- [API Documentation](./docs/api/)
- [User Requirements](./specs/user/)
- [Development Specs](./specs/dev/)

## License

Proprietary
