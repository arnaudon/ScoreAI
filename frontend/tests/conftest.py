"""conftest"""

import os
from pathlib import Path

import pytest
import streamlit as st
from app import db
from app.main import app
from app.users import get_current_user
from fastapi.testclient import TestClient
from pydantic_ai import models
from shared.scores import Score, Scores
from shared.user import User
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

os.environ["DATABASE_PATH"] = "test.db"
pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture(name="frontend_dir")
def frontend_dir_fixture():
    return Path(__file__).resolve().parent.parent


@pytest.fixture(name="session")
def session_fixture():
    """Test session for default db."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_scores")
def test_scores_fixture(frontend_dir):
    """Test scores for default db."""
    score_1 = Score(
        composer="composer",
        title="title_1",
        pdf_path=str(frontend_dir / "tests/data/real_score.pdf"),
        user_id=0,
    )
    score_2 = Score(
        composer="composer", title="title_2", pdf_path=str(frontend_dir / "score_2.pdf"), user_id=0
    )
    score_3 = Score(
        composer="a", title="title_3", pdf_path=str(frontend_dir / "score_3.pdf"), user_id=0
    )
    score_4 = Score(
        composer="a", title="title_4", pdf_path=str(frontend_dir / "score_4.pdf"), user_id=0
    )
    return Scores(scores=[score_1, score_2, score_3, score_4])


@pytest.fixture(name="test_user")
def test_user_fixture():
    """Test user for authenticated requests."""
    return User(username="testuser", email="test@example.com", password="hashed")


@pytest.fixture(name="client")
def client_fixture(session: Session, test_scores: Scores, test_user: User):
    """Client with authenticated user and pre-populated scores."""

    def get_session_override():
        """Override DB session to use test session."""
        return session

    # create a test user that will own all scores
    session.add(test_user)
    session.commit()
    session.refresh(test_user)

    def get_current_user_override():
        """Always return the test user for authentication."""
        return test_user

    app.dependency_overrides[db.get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    client = TestClient(app)

    # add scores to empty db for the authenticated user
    for test_score in test_scores.scores:
        client.post("/scores", json=test_score.model_dump())

    yield client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def request_mock(mocker, client):
    """Mock HTTP client and initialize Streamlit session state for frontend tests."""
    # Ensure a token and user exist in session state so frontend API helpers can
    # build Authorization headers without raising attribute errors.
    if "token" not in st.session_state:
        st.session_state.token = "test-token"
    if "user" not in st.session_state:
        st.session_state.user = "testuser"

    mocker.patch("ui.components.api.requests", new=client)
