#!/bin/bash
set -euo pipefail

# Schema is owned by alembic now — lifespan no longer runs create_all, so
# apply pending migrations before starting the server. Idempotent: alembic
# skips revisions already recorded in ``alembic_version``.
uv run --frozen alembic upgrade head

exec uv run --frozen uvicorn app.main:app --reload --port 8000
