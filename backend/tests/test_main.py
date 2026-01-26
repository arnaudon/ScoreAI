"""test backend main.py"""

import io
import os
from pathlib import Path

import pytest
import sqlalchemy.exc
from fastapi.testclient import TestClient
from sqlmodel import Session

from shared.scores import Score, Scores

backend_dir = Path(__file__).resolve().parent.parent
os.environ["DATA_PATH"] = str(backend_dir / "tests/data")


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
    score = Score(
        composer="another_composer", title="another_title", pdf_path="another_score.pdf", user_id=0
    )
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


def test_delete_score(client: TestClient, test_scores: Scores):
    """test delete score"""

    score = Score(
        composer="yet_another_composer",
        title="yet_another_title",
        pdf_path="yet_another_score.pdf",
        user_id=0,
    )
    response = client.post("/scores", json=score.model_dump())
    response = client.delete(f"/scores/{len(test_scores) + 1}")
    assert response.status_code == 200
    response = client.get("/scores").json()
    assert len(response) == len(test_scores)


def test_delete_not_found_score(client: TestClient, test_scores: Scores):
    """test delete score"""

    score = Score(
        composer="yet_another_composer",
        title="yet_another_title",
        pdf_path="yet_another_score.pdf",
        user_id=0,
    )
    response = client.post("/scores", json=score.model_dump())

    response = client.delete(f"/scores/{len(test_scores) + 1}")
    assert response.status_code == 200
    response = client.get("/scores").json()
    assert len(response) == len(test_scores)


def test_add_play(client: TestClient):
    """test add play"""
    score_id = 1
    response = client.post(f"/scores/{score_id}/play")
    assert response.status_code == 200
    response = client.get("/scores").json()
    assert response[score_id - 1]["number_of_plays"] == 1


def test_add_play_wrong_id(client: TestClient):
    """test add play"""
    score_id = 0
    response = client.post(f"/scores/{score_id}/play")
    assert response.status_code == 200
    response = client.get("/scores").json()


def test_get_pdf(client: TestClient):
    """test get pdf"""
    response = client.get("/pdf/real_score.pdf")
    assert response.status_code == 200


def test_upload_pdf(client: TestClient):
    """test upload pdf"""
    file = io.BytesIO(b"fake_score")
    files = {"file": ("fake_score.pdf", file.getvalue(), "application/pdf")}
    response = client.post("/pdf", files=files)
    assert response.status_code == 200


def test_delete_pdf(client: TestClient):
    """test delete pdf"""
    file = io.BytesIO(b"fake_score")
    files = {"file": ("fake_score.pdf", file.getvalue(), "application/pdf")}
    client.post("/pdf", files=files)
    response = client.delete("/pdf/fake_score.pdf")
    assert response.status_code == 200
    response = client.delete("/pdf/fake_score_not_here.pdf")


# def test_agent(client: TestClient, agent: None):
#    """test agent"""
#    response = client.post("/agent", params={"prompt": "test", "deps": '{"scores": []}'})
#    assert response.status_code == 200
#    result = FullResponse(**response.json())
#    assert isinstance(result.response, Response)
