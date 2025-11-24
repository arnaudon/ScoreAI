import pandas as pd
from streamlit.testing.v1 import AppTest


def test_app():
    """Test app"""
    at = AppTest.from_file("src/scoreai/frontend/app.py")
    at.run()


def test_app_empty_db(mocker):
    """Test app with empty db"""
    at = AppTest.from_file("src/scoreai/frontend/app.py")
    mock_get = mocker.patch("scoreai.frontend.components.api.get_scores_df")
    mock_get.return_value = pd.DataFrame()

    at.run()

    mock_get.assert_called_once()


def test_app_change_lang(mocker):
    """Test app with empty db"""
    at = AppTest.from_file("src/scoreai/frontend/app.py")
    at.run()
    at.sidebar.selectbox("lang").select("en").run()
