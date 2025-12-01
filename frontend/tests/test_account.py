"""Test account"""
from streamlit.testing.v1 import AppTest


def test_account():
    """Test account"""
    at = AppTest.from_file("ui/account.py")
    at.run()
