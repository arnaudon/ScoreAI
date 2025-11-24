"""API module."""

import pandas as pd
import requests
import streamlit as st

from scoreai.config import API_URL
from scoreai.shared_models.responses import FullResponse, Response
from scoreai.shared_models.scores import Scores

_scores = None


class AgentError(Exception):
    """Agent error"""


def reset_score_cache():
    """Reset the score cache"""
    global _scores
    _scores = None


def add_score(score_data) -> dict:
    """Add a score to the db via API"""
    res = requests.post(f"{API_URL}/scores", json=score_data).json()
    reset_score_cache()
    return res


def delete_score(score_id: int):
    """Delete a score from the db via API"""
    requests.delete(f"{API_URL}/scores/{score_id}").json()
    reset_score_cache()


def add_play(score_id: int) -> dict:
    """Add a play to the db via API"""
    res = requests.post(f"{API_URL}/scores/{score_id}/play").json()
    reset_score_cache()
    return res


def get_scores() -> Scores:
    """Get all scores from the db via API"""
    global _scores
    if _scores is None:
        _scores = Scores(scores=requests.get(f"{API_URL}/scores").json())
    return _scores


def get_scores_df() -> pd.DataFrame:
    """Get all scores as dataframe from the db via API"""
    scores = get_scores()
    return pd.DataFrame([s.model_dump() for s in scores.scores])


def run_agent(question: str) -> Response:  # pragma: no cover
    """Run the agent via API"""
    scores = get_scores()
    result = requests.post(
        API_URL + "/agent",
        params={
            "prompt": question,
            "deps": scores.model_dump_json(),
            "message_history": st.session_state.message_history,
        },
    )
    try:
        result = result.json()
    except Exception as exc:
        print("Non-JSON response:", result.text)
        raise AgentError("Something went wrong, try again later") from exc

    full_result = FullResponse(**result)
    st.session_state.message_history.extend(full_result.message_history)
    return full_result.response
