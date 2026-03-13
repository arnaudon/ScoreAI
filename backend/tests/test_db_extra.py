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
