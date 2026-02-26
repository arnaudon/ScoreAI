"""Test the api module."""

import pytest
from shared.scores import Score
from shared.user import User

from ui.components import api

pytestmark = pytest.mark.real_api

# pylint: disable=unused-argument,protected-access


@pytest.fixture(name="mock_get_scores")
def mock_get_scores_fixture(mocker, test_scores):
    """Mock the get_scores function."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = test_scores.model_dump()["scores"]
    mocker.patch("ui.components.api.requests.get", return_value=mock_response)


@pytest.fixture(name="mock_add_score")
def mock_add_score_fixture(mocker, mock_get_scores, other_score):
    """Mock the add_score function."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = other_score.model_dump()
    mocker.patch("ui.components.api.requests.post", return_value=mock_response)


def test_get_scores(mock_get_scores):
    """Test the get_scores function."""

    scores = api.get_scores()
    assert len(scores.scores) > 0


def test_get_scores_df(mock_get_scores):
    """Test the get_scores function."""
    scores_df = api.get_scores_df()
    assert len(scores_df.index) > 0


@pytest.fixture(name="other_score")
def other_score_fixture():
    """Return another score."""
    return Score(
        user_id=0,
        composer="another_composer",
        title="another_title",
        pdf_path="another_score.pdf",
    )


def test_add_score(mocker, mock_get_scores, mock_add_score, other_score):
    """Test the add_score function."""

    # load _SCORES
    api.get_scores()
    assert api._SCORES is not None
    response = api.add_score(score_data=other_score)
    # ensure its refreshed
    assert api._SCORES is None

    assert response["composer"] == other_score.composer
    assert response["title"] == other_score.title
    assert response["pdf_path"] == other_score.pdf_path


def test_reset_score_cache(mock_get_scores):
    """Test the reset_score_cache function."""
    api.get_scores()
    assert api._SCORES is not None
    api.reset_score_cache()
    assert api._SCORES is None


def test_delete_score(mocker, mock_get_scores, mock_add_score, other_score):
    """Test the delete_score function."""
    api.add_score(score_data=other_score)

    api.get_scores()
    assert api._SCORES is not None

    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mocker.patch("ui.components.api.requests.delete", return_value=mock_response)

    api.delete_score({"id": other_score.id, "pdf_path": other_score.pdf_path})
    assert api._SCORES is None


def test_add_play(mocker, mock_get_scores):
    """Test the add_play function."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"number_of_plays": 1}
    mocker.patch("ui.components.api.requests.post", return_value=mock_response)

    api.get_scores()
    assert api._SCORES is not None

    response = api.add_play(score_id=1)
    assert response["number_of_plays"] == 1
    assert api._SCORES is None


# def test_run_agent(client: TestClient, agent: None):
#    """Test the run_agent function."""
#    if "message_history" not in st.session_state:
#        st.session_state.message_history = []
#    response = api.run_agent("test", client=client)
#    assert isinstance(response, Response)


@pytest.fixture(name="test_user")
def test_user_fixture():
    """Test user for default db."""
    return User(username="alice", password="secret")


def test_register_user_calls_backend(mocker, test_user):
    """register_user should POST user JSON to /users endpoint."""
    mock_requests = mocker.patch("ui.components.api.requests")
    api.register_user(test_user)

    mock_requests.post.assert_called_once_with(
        f"{api.API_URL}/users", json=test_user.model_dump(), timeout=30
    )


def test_login_user_calls_backend(mocker):
    """login_user should POST credentials to /token endpoint."""
    mock_requests = mocker.patch("ui.components.api.requests")

    api.login_user("bob", "pw")

    mock_requests.post.assert_called_once_with(
        f"{api.API_URL}/token",
        data={"username": "bob", "password": "pw"},
        timeout=30,
    )


def test_is_admin(mocker):
    """test is_admin"""
    mock_requests = mocker.patch("ui.components.api.requests")
    api.is_admin()

    mock_requests.get.assert_called_once_with(
        f"{api.API_URL}/is_admin",
        headers={"Authorization": "Bearer None"},
        timeout=30,
    )


def test_get_all_users(mocker, test_user):
    """get_all_users should GET all users from /users endpoint."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [test_user.model_dump()]
    mocker.patch("ui.components.api.requests.get", return_value=mock_response)
    users = api.get_all_users()
    assert len(users) == 1
