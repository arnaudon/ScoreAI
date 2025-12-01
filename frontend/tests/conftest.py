"""conftest"""

import os

import pytest
from pydantic_ai import models
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from scoreai.backend import db
from scoreai.backend.main import app
from scoreai.shared_models.scores import Score, Scores

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


@pytest.fixture()
def test_scores():
    """Test scores for default db."""
    score_1 = Score(composer="composer", title="title_1", pdf_path="tests/data/real_score.pdf")
    score_2 = Score(composer="composer", title="title_2", pdf_path="score_2.pdf")
    score_3 = Score(composer="a", title="title_3", pdf_path="score_3.pdf")
    score_4 = Score(composer="a", title="title_4", pdf_path="score_4.pdf")
    return Scores(scores=[score_1, score_2, score_3, score_4])


@pytest.fixture(autouse=True)
def request_mock(mocker, client):
    """Mock client"""
    mocker.patch("scoreai.frontend.components.api.requests", new=client)
