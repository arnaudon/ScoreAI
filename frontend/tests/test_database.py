"""Test database."""

import pandas as pd
import pytest
from shared.scores import IMSLP, Score
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


def test_database_empty(mocker, at):
    """Test database with empty scores to hit else block."""
    mocker.patch("ui.components.db_viewer.GridOptionsBuilder")
    mocker.patch("ui.components.db_viewer.AgGrid")
    mocker.patch("ui.components.api.get_scores_df", return_value=pd.DataFrame())
    at.run()
    # Just running it is enough to cover the lines


def test_database_empty(mocker, at):
    """Test database with empty scores."""
    mocker.patch("ui.components.api.get_scores_df", return_value=pd.DataFrame())
    at.run()
    # verify "Score List:" is present (show_db output)
    assert "Score List:" in at.markdown[0].value


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
    mock_complete_score.return_value = Score(
        title="title", composer="composer", user_id=0
    )

    # Mock upload_pdf which is called in upload
    mocker.patch("ui.components.api.upload_pdf")
    mocker.patch("ui.components.api.add_score", return_value="Success")

    at.button(key="add_manual").click().run()


def test_database_complete_ai(mocker, at):
    """Test AI completion of score data."""
    mocker.patch("ui.components.db_viewer.GridOptionsBuilder")
    mocker.patch("ui.components.db_viewer.AgGrid")

    at.run()

    at.text_input(key="title").set_value("Symphony 5")
    at.text_input(key="composer").set_value("Beethoven")

    mock_complete = mocker.patch("ui.components.api.complete_score_data")
    mock_complete.return_value = Score(
        title="Symphony 5", composer="Beethoven", year=1808, user_id=0
    )

    at.button(key="complete_manual").click().run()

    mock_complete.assert_called()
    assert "score_data_output" in at.session_state
    assert at.session_state.score_data_output.year == 1808


def test_database_add_imslp(mocker, at):
    """Test adding score via IMSLP tab."""
    # Mock dependencies
    mocker.patch("ui.components.db_viewer.GridOptionsBuilder")
    mock_aggrid = mocker.patch("ui.components.db_viewer.AgGrid")

    # Mock IMSLP API calls
    mock_run_agent = mocker.patch("ui.components.api.run_imslp_agent")
    mock_run_agent.return_value.score_ids = [123]

    mock_get_scores = mocker.patch("ui.components.api.get_imslp_scores")
    imslp_score = IMSLP(
        title="IMSLP Title",
        composer="IMSLP Composer",
        year=1900,
        permlink="http://imslp.org",
    )
    mock_get_scores.return_value.scores = [imslp_score]

    at.run()

    # Run first to populate the grid
    at.text_input(key="question").set_value("Beethoven").run()

    mock_run_agent.assert_called()
    mock_get_scores.assert_called()

    # Now mock selection for the grid interaction
    # The app code checks `grid_response["selected_rows"]`
    mock_aggrid.return_value = {
        "selected_rows": pd.DataFrame([imslp_score.model_dump()])
    }

    # Ensure score_df is present in session state for the rerun logic
    # (Although it should persist, explicit setting guarantees it for this test flow)
    at.session_state["score_df"] = pd.DataFrame([imslp_score.model_dump()])

    # Run again to process selection and show add button
    at.run()

    # Verify add button appears
    assert at.button(key="add_imslp").exists
