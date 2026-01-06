#!/usr/bin/env bash
set -e

# This script runs during PostgreSQL container initialization
# It interpolates environment variables into SQL commands for security

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB:-postgres}" <<-EOSQL
    CREATE DATABASE db;

    -- Keycloak
    -- Password is injected via environment variable for security
    CREATE USER keycloak WITH PASSWORD '${KEYCLOAK_DB_PASSWORD}' CREATEDB;
    CREATE DATABASE keycloak;
EOSQL

# Connect to keycloak database and set up permissions
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "keycloak" <<-EOSQL
    -- Grant permissions on the public schema to the keycloak user
    GRANT ALL ON SCHEMA public TO keycloak;
    GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;

    -- For PostgreSQL 15+, also grant default privileges
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO keycloak;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO keycloak;
EOSQL
