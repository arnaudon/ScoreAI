"""test reader"""

from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture(name="at")
def app_test(frontend_dir) -> AppTest:
    at = AppTest.from_file(frontend_dir / "ui" / "reader.py")
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"
    return at


def test_reader_no_score(at):
    """Test reader with no score"""
    at.run()


def test_reader_with_score(test_scores, at):
    """Test reader with score"""
    at.session_state["selected_row"] = pd.Series(test_scores.scores[0].model_dump())
    at.run()
