"""test backend main.py"""

import io
import logging
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import configure_logging
from shared.scores import Score, Scores

backend_dir = Path(__file__).resolve().parent.parent
os.environ["DATA_PATH"] = str(backend_dir / "tests/data")


def test_get_score(client: TestClient, test_scores: Scores):
    """test get score"""
    response = client.get("/scores")
    assert response.status_code == 200
    for score, score_data in zip(test_scores.scores, response.json(), strict=False):
        assert score.composer == score_data["composer"]
        assert score.title == score_data["title"]
        assert score.pdf_path == score_data["pdf_path"]


def test_add_wrong_score(client: TestClient):
    """POST /scores rejects payloads missing required fields with 422."""
    response = client.post("/scores", json={"composer": "another_composer"})
    assert response.status_code == 422

    response = client.post("/scores", json={})
    assert response.status_code == 422


def test_add_score(client: TestClient, test_scores: Scores):
    """test add score"""
    score = Score(
        composer="another_composer",
        title="another_title",
        pdf_path="another_score.pdf",
        user_id=0,
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
    for score, score_data in zip(test_scores.scores, response.json(), strict=False):
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


def test_configure_logging(monkeypatch: pytest.MonkeyPatch):
    """test logging configuration honors LOG_LEVEL env var"""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    configure_logging()
    assert logging.getLogger().level == logging.DEBUG


def test_health_ok(client: TestClient):
    """test /health returns 200 when DB is reachable"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_down(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """test /health returns 503 when DB raises"""

    def boom(*_args, **_kwargs):
        raise RuntimeError("database unreachable")

    monkeypatch.setattr(Session, "execute", boom)
    response = client.get("/health")
    assert response.status_code == 503


def test_add_score_ignores_server_owned_fields(client: TestClient):
    """A client cannot set id, user_id, or number_of_plays on create."""
    payload = {
        "title": "mass assignment title",
        "composer": "mass assignment composer",
        "pdf_path": "x.pdf",
        "id": 999,
        "user_id": 999,
        "number_of_plays": 42,
    }
    response = client.post("/scores", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] != 999
    assert body["user_id"] != 999
    assert body["number_of_plays"] == 0


def test_update_score(client: TestClient):
    """test update score"""
    score = Score(
        composer="update_composer",
        title="update_title",
        pdf_path="update_score.pdf",
        user_id=0,
    )
    response = client.post("/scores", json=score.model_dump())
    assert response.status_code == 200
    score_id = response.json()["id"]

    update_data = {"composer": "updated_composer"}
    response = client.put(f"/scores/{score_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["composer"] == "updated_composer"
    assert response.json()["title"] == "update_title"

    response = client.put("/scores/999999", json=update_data)
    assert response.status_code == 404


# def test_agent(client: TestClient, agent: None):
#    """test agent"""
#    response = client.post("/agent", params={"prompt": "test", "deps": '{"scores": []}'})
#    assert response.status_code == 200
#    result = FullResponse(**response.json())
#    assert isinstance(result.response, Response)
