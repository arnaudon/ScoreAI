"""Database module."""

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///database/app.db"

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Initialize database."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
