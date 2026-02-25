"""Database module."""

import os

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/app.db")


def init_db():
    """Initialize database."""
    init_engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(init_engine)


engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_timeout=30,
)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
