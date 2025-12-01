"""conftest"""

import os

import pytest
from fastapi.testclient import TestClient
from pydantic_ai import models
from shared.scores import Score, Scores
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import db
from app.main import app

os.environ["DATABASE_PATH"] = "test.db"
pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


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
def test_scores_fixture():
    """Test scores for default db."""
    score_1 = Score(composer="composer", title="title_1", pdf_path="tests/data/real_score.pdf")
    score_2 = Score(composer="composer", title="title_2", pdf_path="score_2.pdf")
    score_3 = Score(composer="a", title="title_3", pdf_path="score_3.pdf")
    score_4 = Score(composer="a", title="title_4", pdf_path="score_4.pdf")
    return Scores(scores=[score_1, score_2, score_3, score_4])


@pytest.fixture(name="client")
def client_fixture(session: Session, test_scores: Scores):
    """client"""

    def get_session_override():
        """"""
        return session

    app.dependency_overrides[db.get_session] = get_session_override
    client = TestClient(app)

    # add scores to empty db
    for test_score in test_scores.scores:
        client.post("/scores", json=test_score.model_dump())

    yield client

    app.dependency_overrides.clear()
