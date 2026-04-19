"""Database module."""

import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/app.db")
ASYNC_DATABASE_URL = (
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    .replace("postgres://", "postgresql+asyncpg://")
    .replace("sqlite://", "sqlite+aiosqlite://")
)


def init_db():  # pragma: no cover
    """Run ``alembic upgrade head`` against the configured database.

    Kept as a convenience for the SQLite fast-path dev loop (see
    ``backend/scripts/run.sh``). Prod + CI invoke ``alembic upgrade head``
    directly in the deploy / test_docker workflows, so the FastAPI lifespan
    no longer calls this at startup — that avoided the race with
    ``SQLModel.metadata.create_all`` that broke fresh-volume boots.
    """
    from alembic import command  # noqa: PLC0415
    from alembic.config import Config  # noqa: PLC0415

    alembic_ini = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
    cfg = Config(os.path.abspath(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(cfg, "head")


engine = create_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


connect_args = {"prepared_statement_cache_size": 0} if "asyncpg" in ASYNC_DATABASE_URL else {}

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args=connect_args,
)


async def get_async_session():
    """Get async database session."""
    async with AsyncSession(async_engine) as session:
        yield session
