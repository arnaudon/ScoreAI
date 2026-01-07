from pathlib import Path

from shared.responses import Response
from streamlit.testing.v1 import AppTest


def test_agent(mocker, frontend_dir):
    mock_agent = mocker.patch("ui.components.api.run_agent")
    mock_agent.return_value = Response(score_id=1, response="test")
    at = AppTest.from_file(frontend_dir / "ui" / "welcome.py")
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"
    at.run()
    at.text_input[0].input("test").run()
    at.button[1].click().run()
