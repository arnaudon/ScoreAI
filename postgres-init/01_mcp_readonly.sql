-- Creates a SELECT-only Postgres role used by the `mcp-postgres` container.
-- The MCP SSE server runs with --access-mode=restricted, but this script is
-- defense-in-depth: even a prompt-injected INSERT/UPDATE/DELETE can't succeed
-- because the role has no write privileges granted.
--
-- This file is mounted at /docker-entrypoint-initdb.d/ on the `db` service
-- and runs on FIRST initialization only (empty data volume). The postgres
-- entrypoint executes it as `psql -v ON_ERROR_STOP=1 --username $POSTGRES_USER
-- --dbname $POSTGRES_DB`, so we're already connected to the application DB.
--
-- For an existing prod volume, run the equivalent idempotent SQL in
-- infrastructure/mcp-readonly.sql manually once against the live database.

CREATE USER mcp_readonly WITH PASSWORD 'readonly';

GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mcp_readonly;
