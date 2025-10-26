"""API module."""

import pandas as pd
import requests
import streamlit as st

from scoreai.frontend.config import API_URL
from scoreai.shared_models.responses import FullResponse
from scoreai.shared_models.scores import Scores

TIMEOUT = 60


def add_score(score_data) -> dict:
    """Add a score to the db via API"""
    return requests.post(f"{API_URL}/scores", json=score_data, timeout=TIMEOUT).json()


def get_scores() -> Scores:
    """Get all scores from the db via API"""
    return Scores(scores=requests.get(f"{API_URL}/scores", timeout=TIMEOUT).json())


def get_score_df() -> pd.DataFrame:
    """Get all scores as dataframe from the db via API"""
    scores = get_scores()
    return pd.DataFrame([s.model_dump() for s in scores.scores])


def run_agent(question: str):
    """Run the agent via API"""
    scores = get_scores()
    result = requests.post(
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
