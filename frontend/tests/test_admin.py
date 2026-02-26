"""Test admin"""

import pytest
from streamlit.testing.v1 import AppTest


class MockResponse:
    """Mock requests response."""

    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def test_admin_render(frontend_dir, mocker):
    """Smoke-test that admin page renders."""
    ui_path = frontend_dir / "ui" / "admin.py"
    at = AppTest.from_file(str(ui_path))
    at.session_state["token"] = "fake-token"
    at.session_state["is_admin"] = True

    mocker.patch("ui.components.api.get_all_users", return_value=[])
    mocker.patch(
        "ui.components.api.get_imslp_stats",
        return_value={"total_works": 10, "total_composers": 2},
    )

    at.run()
    assert not at.exception


def test_admin_update_imslp(frontend_dir, mocker):
    """Test starting IMSLP update."""
    ui_path = frontend_dir / "ui" / "admin.py"
    at = AppTest.from_file(str(ui_path))
    at.session_state["token"] = "fake-token"

    mocker.patch("ui.components.api.get_all_users", return_value=[])
    mocker.patch(
        "ui.components.api.get_imslp_stats",
        return_value={"total_works": 10, "total_composers": 2},
    )
    mock_start = mocker.patch(
        "ui.components.api.start_imslp_update", return_value=MockResponse({})
    )

    at.run()

    found = False
    for btn in at.button:
        if btn.label == "Update IMSLP database":
            btn.click().run()
            found = True
            break
    assert found

    mock_start.assert_called()
    assert at.session_state["monitoring"] is True


def test_admin_delete_imslp(frontend_dir, mocker):
    """Test emptying IMSLP database."""
    ui_path = frontend_dir / "ui" / "admin.py"
    at = AppTest.from_file(str(ui_path))
    at.session_state["token"] = "fake-token"

    mocker.patch("ui.components.api.get_all_users", return_value=[])
    mocker.patch(
        "ui.components.api.get_imslp_stats",
        return_value={"total_works": 10, "total_composers": 2},
    )
    mock_empty = mocker.patch(
        "ui.components.api.empty_imslp_database", return_value=MockResponse({})
    )

    at.run()
    
    # Check delete button exists (inside popover)
    if at.button(key="delete"):
        at.button(key="delete").click().run()
        mock_empty.assert_called()


def test_admin_monitoring(frontend_dir, mocker):
    """Test monitoring progress."""
    ui_path = frontend_dir / "ui" / "admin.py"
    at = AppTest.from_file(str(ui_path))
    at.session_state["token"] = "fake-token"
    at.session_state["monitoring"] = True

    mocker.patch("ui.components.api.get_all_users", return_value=[])
    mocker.patch(
        "ui.components.api.get_imslp_stats",
        return_value={"total_works": 10, "total_composers": 2},
    )
    
    # Mock progress to return running then completed
    mock_progress = mocker.patch("ui.components.api.get_imslp_progress")
    mock_progress.side_effect = [
        {"page": 1, "total": 10, "status": "running"},
        {"page": 10, "total": 10, "status": "completed"},
    ]
    
    mock_sleep = mocker.patch("time.sleep")
    
    at.run()
    
    # If logic works, monitoring should be False after completion
    assert at.session_state["monitoring"] is False
    assert at.session_state["finished"] is True
