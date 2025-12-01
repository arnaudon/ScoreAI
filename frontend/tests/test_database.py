import os

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from ui.components import db_viewer


@pytest.fixture
def at():
    """Create a Streamlit app test object."""
    return AppTest.from_file("ui/database.py")


def test_database(at):
    at.run()


def test_database_selected_score(test_scores, mocker, at):
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    mock_response.assert_called_once()


def test_database_selected_score_delete(test_scores, mocker, at):
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    at.button("delete").click().run()


def test_database_selected_score_cancel(test_scores, mocker, at):
    mock_response = mocker.patch("ui.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    at.button("cancel").click().run()


def test_database_add_score(mocker, at):
    db_viewer.DATA_PATH = "tests/data"
    at.run()

    class mock_upload:
        def getbuffer(self):
            return bytes()

    mock_uploader = mocker.patch("ui.components.db_viewer.st.file_uploader")

    # try without file
    mock_uploader.return_value = None
    at.text_input("title").set_value("title")
    at.text_input("composer").set_value("composer")
    at.button("add").click().run()

    # normal run
    mock_uploader.return_value = mock_upload()
    at.text_input("title").set_value("title")
    at.text_input("composer").set_value("composer")
    at.button("add").click().run()

    # try again the same
    at.text_input("title").set_value("title")
    at.text_input("composer").set_value("composer")
    at.button("add").click().run()
    os.remove("tests/data/title_composer.pdf")
