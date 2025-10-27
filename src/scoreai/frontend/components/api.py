"""API module."""

from typing import Any

import pandas as pd
import requests
import streamlit as st

from scoreai.frontend.config import API_URL
from scoreai.shared_models.responses import FullResponse, Response
from scoreai.shared_models.scores import Scores

TIMEOUT = 60
_scores = None


def add_score(score_data, client: Any = requests) -> dict:
    """Add a score to the db via API"""
    return client.post(f"{API_URL}/scores", json=score_data, timeout=TIMEOUT).json()


def reset_score_cache():
    """Reset the score cache"""
    global _scores
    _scores = None


def get_scores(client: Any = requests) -> Scores:
    """Get all scores from the db via API"""
    global _scores
    if _scores is None:
        _scores = Scores(scores=client.get(f"{API_URL}/scores", timeout=TIMEOUT).json())
    return _scores


def get_scores_df(client: Any = requests) -> pd.DataFrame:
    """Get all scores as dataframe from the db via API"""
    scores = get_scores(client=client)
    return pd.DataFrame([s.model_dump() for s in scores.scores])


def run_agent(question: str, client: Any = requests) -> Response:
    """Run the agent via API"""
    scores = get_scores(client=client)
    result = client.post(
        API_URL + "/agent",
        params={
            "prompt": question,
            "deps": scores.model_dump_json(),
            "message_history": st.session_state.message_history,
        },
        timeout=TIMEOUT,
    ).json()

    result = FullResponse(**result)
    st.session_state.message_history.extend(result.message_history)
    return result.response
