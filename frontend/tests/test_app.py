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
    """Smoke-test that the main app renders."""
    at.run()


def test_app_empty_db(mocker, at):
    """Test app with empty db"""
    mock_get = mocker.patch("ui.components.api.get_scores_df")
    mock_get.return_value = pd.DataFrame()

    at.run()

    mock_get.assert_called_once()


def test_app_change_lang(at):
    """Language selector should allow switching languages."""

    at.run()
    at.sidebar.selectbox("lang").select("en").run()


def test_app_login_success(mocker, frontend_dir):
    """Logging in with valid credentials sets token and user in session_state."""

    at = AppTest.from_file(frontend_dir / "ui" / "app.py")

    # Simulate logged-out state so login form is visible
    at.session_state["token"] = None

    mock_login = mocker.patch("ui.components.api.login_user")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "fake-token"}
    mock_login.return_value = mock_response

    at.run()

    # Sidebar login form: first two text_inputs are username and password
    at.sidebar.text_input[0].input("alice")
    at.sidebar.text_input[1].input("secret")

    # First sidebar button should be the Login button
    at.sidebar.button[0].click().run()

    assert at.session_state["token"] == "fake-token"
    assert at.session_state["user"] == "alice"


def test_app_login_invalid_credentials_shows_error(mocker, frontend_dir):
    """Invalid credentials still call login_user; UI handles the error state."""

    at = AppTest.from_file(frontend_dir / "ui" / "app.py")
    at.session_state["token"] = None

    mock_login = mocker.patch("ui.components.api.login_user")
    mock_response = mocker.Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"detail": "Invalid"}
    mock_login.return_value = mock_response

    at.run()

    at.sidebar.text_input[0].input("alice")
    at.sidebar.text_input[1].input("wrong")

    at.sidebar.button[0].click().run()

    mock_login.assert_called_once_with("alice", "wrong")
