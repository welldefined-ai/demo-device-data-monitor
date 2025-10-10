#!/bin/bash
# Database reset script

set -e

echo "Resetting database..."

# Drop and recreate database
docker compose down -v
docker compose up -d db

# Wait for database to be ready
echo "Waiting for database..."
sleep 5

# Run migrations
cd backend
alembic upgrade head
cd ..

echo "Database reset complete!"
