-- One-time setup for existing Postgres deployments (where the
-- docker-entrypoint-initdb.d script in ../postgres-init/01_mcp_readonly.sql
-- never ran because the data volume already existed).
--
-- Usage, e.g. from the Infomaniak VPS:
--
--   docker exec -i postgres_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
--     < infrastructure/mcp-readonly.sql
--
-- Safe to run multiple times — idempotent via DO block + IF NOT EXISTS.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'mcp_readonly') THEN
        CREATE ROLE mcp_readonly LOGIN PASSWORD 'readonly';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE current_database() TO mcp_readonly;
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mcp_readonly;
