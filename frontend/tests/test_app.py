"""Test app"""

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture(name="at")
def app_test(frontend_dir) -> AppTest:
    at = AppTest.from_file(frontend_dir / "ui" / "app.py")
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"
    return at


def test_app(at):
    """Test app"""
    at.run()


def test_app_empty_db(mocker, at):
    """Test app with empty db"""
    mock_get = mocker.patch("ui.components.api.get_scores_df")
    mock_get.return_value = pd.DataFrame()

    at.run()

    mock_get.assert_called_once()


def test_app_change_lang(at):
    """Test app with empty db"""

    at.run()
    at.sidebar.selectbox("lang").select("en").run()
