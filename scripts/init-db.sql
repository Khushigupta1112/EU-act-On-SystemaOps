-- =============================================================================
-- SystemaOps AI Compliance Platform — PostgreSQL Initialization
-- =============================================================================
-- This script runs ONCE on first container start (via docker-entrypoint-initdb.d).
-- It creates the test database alongside the main application database and
-- configures required extensions.
--
-- The primary `systemaops` database and `systemaops` user are created
-- automatically by the POSTGRES_DB / POSTGRES_USER environment variables.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Test database — mirrors production schema; used by pytest
-- ---------------------------------------------------------------------------
CREATE DATABASE systemaops_test
    WITH OWNER = systemaops
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

COMMENT ON DATABASE systemaops_test IS
    'SystemaOps test database — populated and torn down by pytest fixtures';

GRANT ALL PRIVILEGES ON DATABASE systemaops_test TO systemaops;

-- ---------------------------------------------------------------------------
-- Enable extensions on the main database
-- ---------------------------------------------------------------------------
\connect systemaops;

-- UUID generation (used as primary keys for all tenant-isolated entities)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Cryptographic functions (password hashing utilities if needed at DB level)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Full-text search acceleration (used for AI model and policy search)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Case-insensitive text type (email addresses)
CREATE EXTENSION IF NOT EXISTS "citext";

-- ---------------------------------------------------------------------------
-- Enable extensions on the test database
-- ---------------------------------------------------------------------------
\connect systemaops_test;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "citext";

-- ---------------------------------------------------------------------------
-- Performance settings (applied at session level for development)
-- These should be set at the postgresql.conf level in production.
-- ---------------------------------------------------------------------------
\connect systemaops;

-- Log slow queries (> 100ms) in development
ALTER DATABASE systemaops SET log_min_duration_statement = 100;

-- Use a consistent timezone
ALTER DATABASE systemaops SET timezone = 'UTC';
ALTER DATABASE systemaops_test SET timezone = 'UTC';
