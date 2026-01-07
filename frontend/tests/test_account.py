"""Test account"""

from streamlit.testing.v1 import AppTest


def test_account(frontend_dir):
    """Test account"""
    ui_path = frontend_dir / "ui" / "account.py"
    at = AppTest.from_file(str(ui_path))
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"

    at.run()
