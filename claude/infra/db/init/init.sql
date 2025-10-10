-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Database initialization
-- Tables will be created by Alembic migrations
-- This file is for TimescaleDB-specific setup

-- Example: Create retention policy (to be applied after table creation)
-- SELECT add_retention_policy('device_data', INTERVAL '90 days');
