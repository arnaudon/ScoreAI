"""Extended tests for API module to improve coverage."""

import pytest
import requests
from ui.components import api
from shared.scores import Score


class MockResponse:
    """Mock requests response."""

    def __init__(self, json_data, status_code=200, text=""):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self.json_data


def test_add_score(mocker):
    """Test add_score."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_post = mocker.patch("requests.post")
    mock_post.return_value = MockResponse({"status": "ok"})
    
    score = Score(title="T", composer="C", user_id=1)
    res = api.add_score(score)
    
    assert res == {"status": "ok"}
    mock_post.assert_called_once()


def test_run_imslp_agent_success(mocker):
    """Test run_imslp_agent success."""
    # Use a real dict-like object for session state or just standard MagicMock behavior
    mock_history = []
    mocker.patch("streamlit.session_state", mocker.MagicMock())
    api.st.session_state.message_history = mock_history
    api.st.session_state.get.return_value = "fake-token"
    
    mock_post = mocker.patch("requests.post")
    # Message history needs to match Pydantic AI message structure (kind discriminator)
    mock_message = {
        "kind": "request",
        "parts": [{"content": "hi", "part_kind": "user-prompt"}]
    }
    mock_post.return_value = MockResponse({
        "response": {"response": "Found", "score_ids": [1]},
        "message_history": [mock_message]
    })
    
    res = api.run_imslp_agent("query")
    
    assert res.response == "Found"
    assert res.score_ids == [1]
    assert len(mock_history) == 1


def test_run_imslp_agent_error(mocker):
    """Test run_imslp_agent error."""
    mock_state = mocker.MagicMock()
    mock_state.message_history = []
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_post = mocker.patch("requests.post")
    mock_post.return_value = MockResponse({}, status_code=500, text="Error")
    # Mock json() to raise exception to trigger the except block
    mock_post.return_value.json = mocker.Mock(side_effect=Exception("JSON error"))
    
    with pytest.raises(api.AgentError):
        api.run_imslp_agent("query")


def test_run_agent_error(mocker):
    """Test run_agent error."""
    mock_state = mocker.MagicMock()
    mock_state.message_history = []
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mocker.patch("ui.components.api.get_scores") # Mock get_scores
    mock_post = mocker.patch("requests.post")
    mock_post.return_value = MockResponse({}, status_code=500, text="Error")
    mock_post.return_value.json = mocker.Mock(side_effect=Exception("JSON error"))
    
    with pytest.raises(api.AgentError):
        api.run_agent("query")


def test_is_admin(mocker):
    """Test is_admin."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value = MockResponse(True)
    
    assert api.is_admin() is True


def test_get_all_users(mocker):
    """Test get_all_users."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value = MockResponse([
        {"username": "u1", "password": "h"},
        {"username": "u2", "password": "h"}
    ])
    
    df = api.get_all_users()
    assert "password" not in df.columns
    assert len(df) == 2


def test_complete_score_data(mocker):
    """Test complete_score_data."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_post = mocker.patch("requests.post")
    score_data = {"title": "T", "composer": "C", "year": 2000, "user_id": 1}
    mock_post.return_value = MockResponse(score_data)
    
    score = Score(title="T", composer="C", user_id=1)
    completed = api.complete_score_data(score)
    
    assert completed.year == 2000


def test_upload_pdf_success(mocker):
    """Test upload_pdf success."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_post = mocker.patch("requests.post")
    mock_post.return_value = MockResponse({"id": "file1"})
    
    mock_file = mocker.Mock()
    mock_file.getvalue.return_value = b"pdf"
    
    res = api.upload_pdf(mock_file, "file.pdf")
    assert res == {"id": "file1"}


def test_upload_pdf_failure(mocker):
    """Test upload_pdf failure."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_post = mocker.patch("requests.post")
    mock_post.return_value = MockResponse({}, status_code=400)
    
    mock_file = mocker.Mock()
    mock_file.getvalue.return_value = b"pdf"
    
    res = api.upload_pdf(mock_file, "file.pdf")
    assert res is None


def test_get_pdf_url(mocker):
    """Test get_pdf_url."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    # Mock environment variables if needed, but defaults are set in api.py
    
    url = api.get_pdf_url("file1.pdf")
    assert "viewer.html?file=" in url
    assert "file1.pdf" in url
    assert "token%3Dfake-token" in url


def test_imslp_functions(mocker):
    """Test miscellaneous IMSLP functions."""
    mock_state = mocker.MagicMock()
    mock_state.get.return_value = "fake-token"
    mocker.patch("streamlit.session_state", mock_state)
    
    mock_post = mocker.patch("requests.post")
    mock_get = mocker.patch("requests.get")
    
    mock_post.return_value = MockResponse({"status": "ok"})
    mock_get.return_value = MockResponse({"stats": "ok"})
    
    api.start_imslp_update(10)
    assert mock_post.called
    
    api.get_imslp_progress()
    assert mock_post.called
    
    api.cancel_imslp()
    assert mock_post.called
    
    api.get_imslp_stats()
    assert mock_get.called
    
    api.empty_imslp_database()
    assert mock_post.called
