"""test reader"""

import pandas as pd
from streamlit.testing.v1 import AppTest


def test_reader_no_score():
    """Test reader with no score"""
    at = AppTest.from_file("ui/reader.py")
    at.run()


def test_reader_with_score(test_scores):
    """Test reader with score"""
    at = AppTest.from_file("ui/reader.py")
    at.session_state["selected_row"] = pd.Series(test_scores.scores[0].model_dump())
    at.run()
