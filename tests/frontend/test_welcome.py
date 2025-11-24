from streamlit.testing.v1 import AppTest


def test_welcome():
    at = AppTest.from_file("src/scoreai/frontend/welcome.py")
    at.run()
