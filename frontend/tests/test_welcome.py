"""Test welcome"""

from streamlit.testing.v1 import AppTest


def test_welcome(frontend_dir):
    """Test welcome"""
    at = AppTest.from_file(frontend_dir / "ui" / "welcome.py")
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"
    at.run()
