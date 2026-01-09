"""Test database."""

import os

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture(name="at")
def app_test(frontend_dir) -> AppTest:
    """App test fixture"""
    at = AppTest.from_file(frontend_dir / "ui" / "database.py")
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"
    return at


def test_database(at):
    """Test database."""
    at.run()


def test_database_selected_score(test_scores, mocker, at):
    """Test database selected score."""
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    mock_response.assert_called_once()


def test_database_selected_score_delete(test_scores, mocker, at):
    """Test database selected score delete."""
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[1].model_dump()])
    }
    at.run()
    at.button("delete").click().run()


def test_database_selected_score_cancel(test_scores, mocker, at):
    """Test database selected score cancel."""
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    at.button("cancel").click().run()


def test_database_add_score(mocker, at, frontend_dir):
    """Test database add score."""
    at.run()

    class MockUpload:  # pylint: disable=R0903
        """Mock upload."""

        def getbuffer(self):
            """Get buffer."""
            return bytes()

    mock_uploader = mocker.patch("ui.components.db_viewer.st.file_uploader")

    # try without file
    mock_uploader.return_value = None
    at.text_input("title").set_value("title")
    at.text_input("composer").set_value("composer")
    at.button("add").click().run()

    # normal run
    mock_uploader.return_value = MockUpload()
    at.text_input("title").set_value("title")
    at.text_input("composer").set_value("composer")
    at.button("add").click().run()

    # try again the same
    at.text_input("title").set_value("title")
    at.text_input("composer").set_value("composer")
    at.button("add").click().run()
    os.remove(frontend_dir / "tests/data/title_composer_fake-user.pdf")
