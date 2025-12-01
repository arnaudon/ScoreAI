"""Test welcome"""
from streamlit.testing.v1 import AppTest


def test_welcome():
    """Test welcome"""
    at = AppTest.from_file("ui/welcome.py")
    at.run()
