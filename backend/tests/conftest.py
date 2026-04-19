"""conftest"""

import contextlib
import glob
import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient
from pydantic_ai import models
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app import db
from app.main import app, get_pdf_user
from app.users import get_current_user
from shared.scores import Score, Scores
from shared.user import User

os.environ["DATABASE_PATH"] = "test.db"
pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_pdfs():
    """Clean up generated PDFs after tests."""
    yield
    for file in glob.glob("tests/data/*.pdf"):
        if os.path.basename(file) != "real_score.pdf":
            with contextlib.suppress(OSError):
                os.remove(file)


@pytest.fixture(name="db_file")
def db_file_fixture():
    """Temp sqlite file visible to both the sync TestClient and async session fixtures."""
    path = os.path.join(tempfile.gettempdir(), f"scoreguide_test_{uuid.uuid4().hex}.db")
    yield path
    with contextlib.suppress(OSError):
        os.remove(path)


@pytest.fixture(name="session")
def session_fixture(db_file):
    """Sync session against a shared sqlite file so async endpoints see the same rows."""
    engine = create_engine(f"sqlite:///{db_file}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="async_session_factory")
def async_session_factory_fixture(db_file):
    """Async session factory sharing the same sqlite file as the sync session."""
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}")
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory


@pytest.fixture(name="test_scores")
def test_scores_fixture():
    """Test scores for default db."""
    score_1 = Score(
        composer="composer",
        title="title_1",
        pdf_path="tests/data/real_score.pdf",
        user_id=0,
    )
    score_2 = Score(composer="composer", title="title_2", pdf_path="score_2.pdf", user_id=0)
    score_3 = Score(composer="a", title="title_3", pdf_path="score_3.pdf", user_id=0)
    score_4 = Score(composer="a", title="title_4", pdf_path="score_4.pdf", user_id=0)
    return Scores(scores=[score_1, score_2, score_3, score_4])


@pytest.fixture(name="test_user")
def test_user_fixture():
    """Test user for default db."""
    return User(username="testuser", email="test@example.com", password="hashed")


@pytest.fixture(name="client")
def client_fixture(
    session: Session,
    async_session_factory,
    test_scores: Scores,
    test_user: User,
):
    """client with authenticated user"""

    def get_session_override():
        """Override DB session to use test session."""
        return session

    async def get_async_session_override():
        """Yield a fresh async session bound to the same sqlite file."""
        async with async_session_factory() as async_session:
            yield async_session

    # create a test user that will own all scores
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    def get_current_user_override():
        """Always return the test user for authentication."""
        return test_user

    app.dependency_overrides[db.get_session] = get_session_override
    app.dependency_overrides[db.get_async_session] = get_async_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    app.dependency_overrides[get_pdf_user] = get_current_user_override

    # Seed scores directly via the session instead of POSTing them through the
    # HTTP API — avoids a per-test startup tax of N HTTP requests.
    for test_score in test_scores.scores:
        test_score.user_id = test_user.id
        session.add(test_score)
    session.commit()
    for test_score in test_scores.scores:
        session.refresh(test_score)

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()
