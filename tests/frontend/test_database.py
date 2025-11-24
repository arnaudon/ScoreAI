import os

import pandas as pd
from streamlit.testing.v1 import AppTest

from scoreai.frontend.components import db_viewer


def test_database():
    at = AppTest.from_file("src/scoreai/frontend/database.py")
    at.run()


def test_database_selected_score(test_scores, mocker):
    at = AppTest.from_file("src/scoreai/frontend/database.py")
    mock_response = mocker.patch("scoreai.frontend.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    mock_response.assert_called_once()


def test_database_selected_score_delete(test_scores, mocker):
    at = AppTest.from_file("src/scoreai/frontend/database.py")
    mock_response = mocker.patch("scoreai.frontend.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    at.button("delete").click().run()


def test_database_selected_score_cancel(test_scores, mocker):
    at = AppTest.from_file("src/scoreai/frontend/database.py")
    mock_response = mocker.patch("scoreai.frontend.components.db_viewer.AgGrid")
    mock_response.return_value = {
        "selected_rows": pd.DataFrame([test_scores.scores[0].model_dump()])
    }
    at.run()
    at.button("cancel").click().run()


def test_database_add_score(mocker):
    db_viewer.DATA_PATH = "tests/data"
    at = AppTest.from_file("src/scoreai/frontend/database.py")
    at.run()

    class mock_upload:
        def getbuffer(self):
            return bytes()

    mock_uploader = mocker.patch("scoreai.frontend.components.db_viewer.st.file_uploader")

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
