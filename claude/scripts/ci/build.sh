#!/bin/bash
# CI build script

set -e

echo "Building DDMS..."

# Backend tests
echo "Running backend tests..."
cd backend
uv pip install -e ".[dev]"
ruff check .
mypy ddms
pytest --cov=ddms
cd ..

# Frontend tests
echo "Running frontend tests..."
cd frontend
npm ci
npm run lint
npm run build
npm test
cd ..

# Docker build
echo "Building Docker images..."
docker compose build

echo "Build complete!"
