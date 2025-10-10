#!/bin/bash
# Development environment setup script

set -e

echo "Setting up DDMS development environment..."

# Backend setup
echo "Setting up backend..."
cd backend
pip install uv
uv pip install -e ".[dev]"
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

# Copy environment files
echo "Creating environment files..."
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

echo "Setup complete!"
echo "To start development:"
echo "  Backend: cd backend && uvicorn ddms.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo "  Or use: docker compose up"
