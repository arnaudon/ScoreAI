"""Database module."""

from sqlmodel import Session, SQLModel, create_engine

from scoreai.config import DATABASE_URL


def init_db():
    """Initialize database."""
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        yield session
