"""Database module."""

import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/app.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://").replace("sqlite://", "sqlite+aiosqlite://")


def init_db():  # pragma: no cover
    """Initialize database."""
    init_engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(init_engine)


engine = create_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)


async def get_async_session():
    """Get async database session."""
    async with AsyncSession(async_engine) as session:
        yield session
