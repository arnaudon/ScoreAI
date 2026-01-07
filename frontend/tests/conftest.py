"""conftest"""

import os
from pathlib import Path

import pytest
import streamlit as st

# from app import db
# from app.main import app
# from app.users import get_current_user
# from fastapi.testclient import TestClient
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


@pytest.fixture(autouse=True)
def request_mock(request, mocker, test_scores):
    """Mock api calls."""
    if "real_api" in request.keywords:
        return
    mocker_get_scores = mocker.patch("ui.components.api.get_scores")
    mocker_get_scores.return_value = test_scores

    mocker_add_play = mocker.patch("ui.components.api.add_play")
    mocker_add_play.return_value = {"number_of_plays": 1}
