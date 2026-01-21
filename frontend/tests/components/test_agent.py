"""Test the agent function."""

from shared.responses import Response
from streamlit.testing.v1 import AppTest


def test_agent(mocker, frontend_dir):
    """Test the agent function."""
    mock_agent = mocker.patch("ui.components.api.run_agent")
    mock_agent.return_value = Response(score_id=1, response="test")
    at = AppTest.from_file(frontend_dir / "ui" / "welcome.py")
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"
    at.session_state["user_id"] = 0
    at.run()
    at.text_input("question").input("test").run()
    at.button("open").click().run()
