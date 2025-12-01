from streamlit.testing.v1 import AppTest


def test_account():
    at = AppTest.from_file("src/scoreai/frontend/account.py")
    at.run()
