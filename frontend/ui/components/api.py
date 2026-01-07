"""API module."""

import os

import pandas as pd
import requests
import streamlit as st
from pwdlib import PasswordHash
from shared.responses import FullResponse, Response
from shared.scores import Score, Scores

# from shared.user import User

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
_SCORES = None

password_hash = PasswordHash.recommended()


class AgentError(Exception):
    """Agent error"""


def reset_score_cache():
    """Reset the score cache"""
    global _SCORES
    _SCORES = None


def register_user(new_user):
    """Register a new user via API"""
    response = requests.post(f"{API_URL}/users", json=new_user.model_dump())
    return response


def login_user(username, password):
    """Login a user via API"""
    response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    return response


def add_score(score_data: Score) -> dict:
    """Add a score to the db via API"""
    response = requests.post(
        f"{API_URL}/scores",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        json=score_data.model_dump(),
    ).json()
    reset_score_cache()
    return response


def delete_score(score_id: int):
    """Delete a score from the db via API"""
    requests.delete(
        f"{API_URL}/scores/{score_id}",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
    )
    reset_score_cache()


def add_play(score_id: int) -> dict:
    """Add a play to the db via API"""
    res = requests.post(
        f"{API_URL}/scores/{score_id}/play",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
    ).json()
    reset_score_cache()
    return res


def get_scores() -> Scores:
    """Get all scores from the db via API"""
    global _SCORES
    if _SCORES is None:
        _SCORES = Scores(
            scores=requests.get(
                f"{API_URL}/scores",
                headers={"Authorization": f"Bearer {st.session_state.get("token")}"},
            ).json()
        )
    return _SCORES


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
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
    )
    try:
        result = result.json()
    except Exception as exc:
        print("Non-JSON response:", result.text)
        raise AgentError("Something went wrong, try again later") from exc

    full_result = FullResponse(**result)
    st.session_state.message_history.extend(full_result.message_history)
    return full_result.response
