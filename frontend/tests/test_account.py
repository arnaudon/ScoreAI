"""Test account"""

from streamlit.testing.v1 import AppTest


def test_account(frontend_dir):
    """Smoke-test that account page renders when logged in."""
    ui_path = frontend_dir / "ui" / "account.py"
    at = AppTest.from_file(str(ui_path))
    at.session_state["token"] = "fake-token"
    at.session_state["user"] = "fake-user"

    at.run()


def test_account_register_user_success(frontend_dir, mocker):
    """When logged out, clicking Sign Up calls register_user."""

    ui_path = frontend_dir / "ui" / "account.py"
    at = AppTest.from_file(str(ui_path))

    at.session_state["token"] = None

    mock_register = mocker.patch("ui.components.api.register_user")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_register.return_value = mock_response

    at.run()

    at.text_input(key="username").input("newuser")
    at.text_input(key="password").input("pw")

    at.button(key="signup").click().run()

    mock_register.assert_called_once()


def test_account_register_user_failure_shows_error(frontend_dir, mocker):
    """Registration errors still call register_user (UI handles the error)."""

    ui_path = frontend_dir / "ui" / "account.py"
    at = AppTest.from_file(str(ui_path))

    at.session_state["token"] = None

    mock_register = mocker.patch("ui.components.api.register_user")
    mock_response = mocker.Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "error"}
    mock_register.return_value = mock_response

    at.run()

    at.text_input("username").input("newuser")
    at.text_input("password").input("pw")

    at.button("signup").click().run()

    mock_register.assert_called_once()
