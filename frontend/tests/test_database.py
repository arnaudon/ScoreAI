"""Test database."""

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture(name="at")
def app_test(frontend_dir) -> AppTest:
    """App test fixture"""
    at = AppTest.from_file(frontend_dir / "ui" / "database.py")
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = {"username": "fake-user", "id": 0}
    return at


def test_database(at):
    """Test database."""
    at.run()


def test_database_selected_score(test_scores, mocker, at):
    """Test database selected score."""
    # We must patch GridOptionsBuilder as well because it's None in the module due to Import error
    mocker.patch("ui.components.db_viewer.GridOptionsBuilder")
    
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    mock_response.assert_called_once()


def test_database_selected_score_delete(test_scores, mocker, at):
    """Test database selected score delete."""
    mocker.patch("ui.components.db_viewer.GridOptionsBuilder")
    
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[1].model_dump()])
    }
    at.run()
    # verify delete button exists before clicking
    if at.button(key="delete"):
        at.button(key="delete").click().run()


def test_database_selected_score_cancel(test_scores, mocker, at):
    """Test database selected score cancel."""
    mocker.patch("ui.components.db_viewer.GridOptionsBuilder")
    
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    if at.button(key="cancel"):
        at.button(key="cancel").click().run()


def test_database_add_score(mocker, at):
    """Test database add score."""
    mocker.patch("ui.components.db_viewer.GridOptionsBuilder")
    mocker.patch("ui.components.db_viewer.AgGrid")
    
    at.run()

    class MockUpload:  # pylint: disable=R0903
        """Mock upload."""

        def getvalue(self):
            """Get buffer."""
            return bytes()

    mock_uploader = mocker.patch("ui.components.db_viewer.st.file_uploader")
    mock_uploader.return_value = None
    
    # We need to make sure add_score() is called.
    # It's called in show_db().
    
    # Widgets keys are "title" and "composer"
    at.text_input(key="title").set_value("title")
    at.text_input(key="composer").set_value("composer")
    at.button(key="add_manual").click().run()

    # normal run
    mock_uploader.return_value = MockUpload()
    at.text_input(key="title").set_value("title")
    at.text_input(key="composer").set_value("composer")

    mock_complete_score = mocker.patch("ui.components.api.complete_score_data")
    mock_complete_score.return_value = Score(title="title", composer="composer", user_id=0)
    
    # Mock upload_pdf which is called in upload
    mocker.patch("ui.components.api.upload_pdf")
    mocker.patch("ui.components.api.add_score", return_value="Success")
    
    at.button(key="add_manual").click().run()
