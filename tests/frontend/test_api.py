import streamlit as st
from fastapi.testclient import TestClient

from scoreai.frontend.components import api
from scoreai.shared_models.responses import Response


def test_get_scores(client: TestClient):
    """Test the get_scores function."""
    scores = api.get_scores(client=client)
    assert len(scores.scores) > 0


def test_get_scores_df(client: TestClient):
    """Test the get_scores function."""
    scores_df = api.get_scores_df(client=client)
    assert len(scores_df.index) > 0


def test_add_score(client: TestClient):
    """Test the add_score function."""
    score = {
        "composer": "another_composer",
        "title": "another_title",
        "pdf_path": "another_score.pdf",
    }
    response = api.add_score(score_data=score, client=client)
    assert response["composer"] == score["composer"]
    assert response["title"] == score["title"]
    assert response["pdf_path"] == score["pdf_path"]


def test_reset_score_cache(client: TestClient):
    """Test the reset_score_cache function."""
    api.get_scores(client=client)
    api.reset_score_cache()
    assert api._scores == None


def test_run_agent(client: TestClient, override_agent: None):
    """Test the run_agent function."""
    if "message_history" not in st.session_state:
        st.session_state.message_history = []
    response = api.run_agent("test", client=client)
    assert isinstance(response, Response)
