# `shared`

SQLModel tables and pydantic response models shared between `backend/` and anything else in the workspace. Importable as `shared.<module>`.

## Modules

- `shared.user` — `User` table (JWT subject, role, credits).
- `shared.scores` — `ScoreBase` (mixin), `Score` (table), `IMSLP` (IMSLP cache table), `ScoreCreate` / `ScoreUpdate` (API request models), `Scores` / `IMSLPScores` (list wrappers).
- `shared.settings` — `Setting` key/value table (runtime-tunable LLM model IDs etc.).
- `shared.responses` — `Response`, `ImslpResponse`, `FullResponse`, `ImslpFullResponse` returned by the agent endpoints.

## Developing

Scoped to this workspace member (mirrors `.github/workflows/test.yml`):

```bash
uv run --frozen --project shared --directory shared pytest
uv run --frozen ruff check shared
uv run --frozen ruff format --check shared
uv run --frozen --project shared --directory shared mypy .
```
