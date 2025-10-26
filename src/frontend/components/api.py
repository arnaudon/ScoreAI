import pandas as pd
import requests
import streamlit as st

from frontend.config import API_URL
from shared_models.responses import FullResponse
from shared_models.score_models import Score, Scores


def add_score(score_data):
    """Add a score to the db via API"""
    return requests.post(f"{API_URL}/scores", json=score_data).json()


def get_scores():
    return Scores(scores=requests.get(f"{API_URL}/scores").json())


def get_score_df():
    scores = get_scores()
    return pd.DataFrame([s.model_dump() for s in scores.scores])


def run_agent(question):
    scores = get_scores()
    result = requests.post(
        API_URL + "/agent",
        params={
            "prompt": question,
            "deps": scores.model_dump_json(),
            "message_history": st.session_state.message_history,
        },
    ).json()

    result = FullResponse(**result)
    st.session_state.message_history.extend(result.message_history)
    return result.response
