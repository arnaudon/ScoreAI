"""API module."""

import json
import logging
import os
from typing import List
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st
from pwdlib import PasswordHash
from shared.responses import FullResponse, ImslpFullResponse, ImslpResponse, Response
from shared.scores import IMSLPScores, Score, Scores
from shared.user import User

logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")
_SCORES = None

password_hash = PasswordHash.recommended()
TIMEOUT = 30


class AgentError(Exception):
    """Agent error"""


def reset_score_cache():
    """Reset the score cache"""
    global _SCORES  # pylint: disable=global-statement
    _SCORES = None


def register_user(new_user: User):
    """Register a new user via API"""
    response = requests.post(f"{API_URL}/users", json=new_user.model_dump(), timeout=TIMEOUT)
    return response


def login_user(username, password):
    """Login a user via API"""
    response = requests.post(
        f"{API_URL}/token",
        data={"username": username, "password": password},
        timeout=TIMEOUT,
    )
    return response


def get_user():
    """Get the current user via API"""
    response = requests.get(
        f"{API_URL}/user",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    ).json()
    return response


def add_score(score_data: Score) -> dict:
    """Add a score to the db via API"""
    response = requests.post(
        f"{API_URL}/scores",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        json=score_data.model_dump(),
        timeout=TIMEOUT,
    ).json()
    reset_score_cache()
    return response


def delete_score(score_data):
    """Delete a score from the db via API"""
    requests.delete(
        f"{API_URL}/scores/{score_data['id']}",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )
    requests.delete(
        f"{API_URL}/pdf/{score_data['pdf_path']}",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )
    reset_score_cache()


def add_play(score_id: int) -> dict:
    """Add a play to the db via API"""
    res = requests.post(
        f"{API_URL}/scores/{score_id}/play",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    ).json()
    reset_score_cache()
    return res


def get_scores() -> Scores:
    """Get all scores from the db via API"""
    global _SCORES  # pylint: disable=global-statement
    if _SCORES is None:
        _SCORES = Scores(
            scores=requests.get(
                f"{API_URL}/scores",
                headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
                timeout=TIMEOUT,
            ).json()
        )
    return _SCORES


def get_scores_df() -> pd.DataFrame:
    """Get all scores as dataframe from the db via API"""
    scores = get_scores()
    df = pd.DataFrame([s.model_dump() for s in scores.scores])
    if "id" in df.columns:
        df.index = df.id
    return df


def run_imslp_agent(question: str) -> ImslpResponse:  # pragma: no cover
    """Run the agent via API"""
    result = requests.post(
        API_URL + "/imslp_agent",
        params={
            "prompt": question,
            "message_history": st.session_state.message_history,
        },
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )
    try:
        result = result.json()
    except Exception as exc:
        print("Non-JSON response:", result.text)
        raise AgentError("Something went wrong, try again later") from exc

    full_result = ImslpFullResponse(**result)
    st.session_state.message_history.extend(full_result.message_history)
    return full_result.response


def get_imslp_scores(score_ids: List[int]) -> IMSLPScores:
    """Get imlsp scores from ids."""
    return IMSLPScores(
        scores=requests.get(
            f"{API_URL}/imslp/scores_by_ids",
            params={"score_ids": json.dumps(score_ids)},
            headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
            timeout=TIMEOUT,
        ).json()
    )


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
        timeout=TIMEOUT,
    )
    try:
        result = result.json()
    except Exception as exc:
        print("Non-JSON response:", result.text)
        raise AgentError("Something went wrong, try again later") from exc

    full_result = FullResponse(**result)
    st.session_state.message_history.extend(full_result.message_history)
    return full_result.response


def is_admin():
    """Check if the user is admin via API"""
    return requests.get(
        f"{API_URL}/is_admin",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    ).json()


def valid_token():
    """Check if the token is valid."""
    result = requests.get(
        f"{API_URL}/is_admin",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )
    if result.status_code == 401:
        return False
    return True


def get_all_users():
    """Get all users from the db via API"""
    users = requests.get(
        f"{API_URL}/users",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    ).json()
    df = pd.DataFrame(users)
    df.drop("password", axis=1, inplace=True)
    return df


def complete_score_data(score: Score):
    """Complete a score with agents"""
    return Score(
        **requests.post(
            f"{API_URL}/complete_score",
            headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
            json=score.model_dump(),
            timeout=TIMEOUT,
        ).json()
    )


def upload_pdf(file, filename):
    """Upload pdf file"""
    files = {"file": (filename, file.getvalue(), "application/pdf")}
    response = requests.post(
        f"{API_URL}/pdf",
        files=files,
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )

    if response.status_code == 200:
        data = response.json()
    else:
        logger.error("Upload failed.")
        data = None
    return data


def get_pdf_url(file_id):
    """Get pdf url"""
    token = st.session_state.get("token", "")
    url = f"{PUBLIC_API_URL}/pdf/{file_id}?token={token}"
    viewer_url = f"{PUBLIC_API_URL}/pdfjs/web/viewer.html"
    return f"{viewer_url}?file={quote(url, safe='')}"


def start_imslp_update(max_pages: int = 260):
    """Update the IMSLP database"""
    return requests.post(
        f"{API_URL}/imslp/start/{max_pages}",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )


def get_imslp_progress():
    """Get the progress of the IMSLP update"""
    return requests.post(
        f"{API_URL}/imslp/progress",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    ).json()


def cancel_imslp():
    """Cancel the IMSLP update"""
    requests.post(
        f"{API_URL}/imslp/cancel",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )


def get_imslp_stats():
    """Get IMSLP stats"""
    return requests.get(
        f"{API_URL}/imslp/stats",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    ).json()


def empty_imslp_database():
    """Empty the IMSLP database"""
    return requests.post(
        f"{API_URL}/imslp/empty",
        headers={"Authorization": f"Bearer {st.session_state.get('token')}"},
        timeout=TIMEOUT,
    )
