"""Additional DB edge case tests for backend/app/db.py."""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from app import db


@pytest.fixture
def temp_engine_fixture(tmp_path):
    """Create a temporary DB engine."""
    dbfile = tmp_path / "testdb.sqlite"
    engine = create_engine(f"sqlite:///{dbfile}")
    SQLModel.metadata.create_all(engine)
    return engine


def test_get_session_context_manager(temp_engine_fixture):  # pylint: disable=redefined-outer-name
    """Test get_session context manager."""
    # Patch db.engine for this test
    orig = db.engine
    db.engine = temp_engine_fixture
    try:
        # Should yield a session without raising
        session_iter = db.get_session()
        session = next(session_iter)
        assert isinstance(session, Session)
    finally:
        db.engine = orig


def test_init_db_creates_tables(tmp_path):
    """Test init_db creates tables."""
    dbfile = tmp_path / "initdb.sqlite"
    engine = create_engine(f"sqlite:///{dbfile}")
    orig_url = db.DATABASE_URL
    db.DATABASE_URL = f"sqlite:///{dbfile}"
    try:
        db.init_db()
        insp = engine.connect().connection
        # SQLite: check at least one table exists
        res = insp.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        assert len(res) > 0
    finally:
        db.DATABASE_URL = orig_url
