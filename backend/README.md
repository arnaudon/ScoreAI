# `backend` — FastAPI + pydantic-ai

Package name: `app`. Entry point: `app.main:app`.

## Layout

- `app/main.py` — FastAPI app, routes for scores, PDFs, three agent endpoints, admin model config, `/health`.
- `app/agent.py` — four pydantic-ai agents (`run_agent`, `run_imslp_agent`, `run_complete_agent`, `run_imslp_complete_agent`) + the `<user_request>` wrapping and `ModelHTTPError` mapping helpers.
- `app/credits.py` — `consume_credit` async context manager with atomic debit/refund (`UPDATE … WHERE credits > 0`).
- `app/users.py` — JWT (`pyjwt` + argon2) auth, `get_current_user` / `get_admin_user` dependencies, `POST /token`, `/user` CRUD.
- `app/imslp.py` — IMSLP scraper + admin endpoints (`/imslp/start`, `/progress`, `/cancel`, `/stats`, `/empty`). Single-worker only (see `Dockerfile.backend`).
- `app/db.py` — sync + async engines; `DATABASE_URL` rewritten for asyncpg/aiosqlite automatically; `NullPool` + `prepared_statement_cache_size=0` for pgbouncer.
- `app/file_helper.py` — S3 ↔ local PDF storage singleton (`S3_ENDPOINT` toggles).
- `app/config.py` — env-driven constants (`MCP_URL`, `AGENT_RATE_LIMIT`, `SUPPORT_EMAIL`, `CORS_ORIGINS`).
- `app/rate_limit.py` — shared `slowapi` `Limiter`.
- `migrations/` — Alembic migrations. `env.py` swaps `db:5432` → `localhost:5432` when not inside docker.

## Commands

```bash
# Tests (99% coverage gate in pytest.ini)
uv run --frozen --project backend --directory backend pytest

# Single test
uv run --project backend --directory backend pytest tests/test_main.py::test_health_ok -q

# Format / lint / type-check
uv run --frozen ruff format --check backend
uv run --frozen ruff check backend
uv run --frozen --project backend --directory backend mypy .

# Local dev (port 8000, --reload)
./scripts/run.sh

# Alembic
uv run --project backend --directory backend alembic revision --autogenerate -m "msg"
uv run --project backend --directory backend alembic upgrade head
```

See `../CLAUDE.md` for architecture details (agent wiring, MCP SQL safety, credit flow).
