"""test backend main.py"""

import pytest
import sqlalchemy.exc
from fastapi.testclient import TestClient
from sqlmodel import Session

from scoreai.backend.main import app
from scoreai.shared_models.responses import FullResponse, Response
from scoreai.shared_models.scores import Score, Scores


def test_get_score(client: TestClient, test_scores: Scores):
    """test get score"""
    response = client.get("/scores")
    assert response.status_code == 200
    for score, score_data in zip(test_scores.scores, response.json()):
        assert score.composer == score_data["composer"]
        assert score.title == score_data["title"]
        assert score.pdf_path == score_data["pdf_path"]


def test_add_wrong_score(client: TestClient, session: Session):
    """test add with missing values"""
    score = {"composer": "another_composer", "title": "another_title"}
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        client.post("/scores", json=score)
    session.rollback()

    score = {"composer": "another_composer"}
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        client.post("/scores", json=score)
    session.rollback()

    score = {}
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        client.post("/scores", json=score)
    session.rollback()


def test_add_score(client: TestClient, test_scores: Scores):
    """test add score"""
    score = Score(composer="another_composer", title="another_title", pdf_path="another_score.pdf")
    response = client.post("/scores", json=score.model_dump())

    data = response.json()
    assert response.status_code == 200
    assert data["composer"] == score.composer
    assert data["title"] == score.title
    assert data["pdf_path"] == score.pdf_path

    # get all scores and check they are all here
    response = client.get("/scores")
    test_scores.scores.append(score)
    assert response.status_code == 200
    for score, score_data in zip(test_scores.scores, response.json()):
        assert score.composer == score_data["composer"]
        assert score.title == score_data["title"]
        assert score.pdf_path == score_data["pdf_path"]


def test_lifespan():
    """test lifespan"""
    with TestClient(app) as client:
        response = client.get("/scores")
    assert response.status_code == 200


def test_agent(client: TestClient, override_agent: None):
    """test agent"""
    response = client.post(
        "/agent", params={"prompt": "tell me something funny", "deps": '{"scores": []}'}
    )
    assert response.status_code == 200
    result = FullResponse(**response.json())
    assert isinstance(result.response, Response)
