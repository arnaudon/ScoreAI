"""Additional DB edge case tests for backend/app/db.py."""

from app import db
from sqlmodel import Session, SQLModel, create_engine
import pytest


@pytest.fixture
def temp_engine(tmp_path):
    dbfile = tmp_path / "testdb.sqlite"
    engine = create_engine(f"sqlite:///{dbfile}")
    SQLModel.metadata.create_all(engine)
    return engine


def test_get_session_context_manager(temp_engine):
    # Patch db.engine for this test
    orig = db.engine
    db.engine = temp_engine
    try:
        # Should yield a session without raising
        session_iter = db.get_session()
        session = next(session_iter)
        assert isinstance(session, Session)
    finally:
        db.engine = orig


def test_init_db_creates_tables(tmp_path):
    dbfile = tmp_path / "initdb.sqlite"
    engine = create_engine(f"sqlite:///{dbfile}")
    orig_url = db.DATABASE_URL
    db.DATABASE_URL = f"sqlite:///{dbfile}"
    try:
        db.init_db()
        insp = engine.connect().connection
        # SQLite: check at least one table exists
        res = insp.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        assert len(res) > 0
    finally:
        db.DATABASE_URL = orig_url
