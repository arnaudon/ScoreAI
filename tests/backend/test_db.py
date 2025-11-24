"""test backend db.py"""

from sqlmodel import Session

from scoreai.backend import db

db.DATABASE_URL = "sqlite:///.test.db"


def test_init_db():
    """test init db"""

    db.init_db()


def test_get_session():
    """test get session"""

    assert isinstance(next(db.get_session()), Session)
