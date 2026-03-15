"""Tests for the agent module."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic_ai.exceptions import ModelHTTPError

from app import agent
from shared.responses import FullResponse, ImslpResponse, Response
from shared.scores import Difficulty, Score, ScoreBase, Scores
from shared.user import User


@pytest.mark.asyncio
async def test_agent_success(test_scores: Scores, test_user: User):
    """test agent happy path with TestModel"""
    result = await agent.run_agent(
        prompt="test", deps=agent.Deps(user=test_user, scores=test_scores), model="test"
    )
    assert isinstance(result, FullResponse)


@pytest.mark.asyncio
async def test_get_score_info():
    """Test get_score_info tool."""
    ctx = MagicMock()
    scores = Scores(scores=[Score(title="test", composer="test")])
    ctx.deps = agent.Deps(user=User(username="test"), scores=scores)
    result = await agent.get_score_info(ctx)
    assert result == f"The scores infos are {scores.model_dump_json()}."


@pytest.mark.asyncio
async def test_get_user_name():
    """Test get_user_name tool."""
    ctx = MagicMock()
    user = User(username="test_user")
    ctx.deps = agent.Deps(user=user, scores=Scores(scores=[]))
    result = await agent.get_user_name(ctx)
    assert result == "test_user"


@pytest.mark.asyncio
async def test_get_random_score_by_composer_found():
    """Test get_random_score_by_composer when a score is found."""
    ctx = MagicMock()
    score = Score(title="test", composer="Bach")
    ctx.deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[score]))
    result = await agent.get_random_score_by_composer(ctx, agent.Filter(composer="Bach"))
    assert result == score.model_dump_json()


@pytest.mark.asyncio
async def test_get_random_score_by_composer_not_found():
    """Test get_random_score_by_composer when no score is found."""
    ctx = MagicMock()
    ctx.deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.get_random_score_by_composer(ctx, agent.Filter(composer="Unknown"))
    assert result == "Not found"


@pytest.mark.asyncio
async def test_get_easiest_score_by_composer_found():
    """Test get_easiest_score_by_composer when scores are found."""
    ctx = MagicMock()
    score_easy = Score(title="Easy", composer="Bach", difficulty=Difficulty.easy, difficulty_int=0)
    score_hard = Score(
        title="Hard", composer="Bach", difficulty=Difficulty.expert, difficulty_int=4
    )
    ctx.deps = agent.Deps(
        user=User(username="test"), scores=Scores(scores=[score_easy, score_hard])
    )
    result = await agent.get_easiest_score_by_composer(ctx, agent.Filter(composer="Bach"))
    assert result == score_easy.model_dump_json()


@pytest.mark.asyncio
async def test_get_easiest_score_by_composer_not_found():
    """Test get_easiest_score_by_composer when no score is found."""
    ctx = MagicMock()
    ctx.deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.get_easiest_score_by_composer(ctx, agent.Filter(composer="Unknown"))
    assert result == "Not found"


@pytest.mark.asyncio
async def test_run_imslp_agent_http_error_429(monkeypatch):
    """Test run_imslp_agent with a 429 HTTP error."""
    mock_agent_run = AsyncMock(side_effect=ModelHTTPError(429, "error"))
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    result = await agent.run_imslp_agent("prompt")
    assert result.response.response == "Rate limit exceeded (Quota hit)"


@pytest.mark.asyncio
async def test_run_imslp_agent_http_error_other(monkeypatch):
    """Test run_imslp_agent with a non-429 HTTP error."""
    err = ModelHTTPError(500, "error")
    mock_agent_run = AsyncMock(side_effect=err)
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    result = await agent.run_imslp_agent("prompt")
    assert result.response.response == "An HTTP error occurred"


@pytest.mark.asyncio
async def test_run_imslp_agent_exception(monkeypatch):
    """Test run_imslp_agent with a generic exception."""
    mock_agent_run = AsyncMock(side_effect=Exception("error"))
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    result = await agent.run_imslp_agent("prompt")
    assert result.response.response == "An unexpected error occurred"


@pytest.mark.asyncio
async def test_run_agent_http_error_429(monkeypatch):
    """Test run_agent with a 429 HTTP error."""
    mock_agent_run = AsyncMock(side_effect=ModelHTTPError(429, "error"))
    mock_agent = MagicMock()
    mock_agent.run = mock_agent_run
    monkeypatch.setattr("app.agent.get_main_agent", lambda *args, **kwargs: mock_agent)
    deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.run_agent("prompt", deps)
    assert result.response.response == "Rate limit exceeded (Quota hit)"


@pytest.mark.asyncio
async def test_run_agent_http_error_other(monkeypatch):
    """Test run_agent with a non-429 HTTP error."""
    err = ModelHTTPError(500, "error")
    mock_agent_run = AsyncMock(side_effect=err)
    mock_agent = MagicMock()
    mock_agent.run = mock_agent_run
    monkeypatch.setattr("app.agent.get_main_agent", lambda *args, **kwargs: mock_agent)
    deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.run_agent("prompt", deps)
    assert result.response.response == "An HTTP error occurred"


@pytest.mark.asyncio
async def test_run_agent_exception(monkeypatch):
    """Test run_agent with a generic exception."""
    mock_agent_run = AsyncMock(side_effect=Exception("error"))
    mock_agent = MagicMock()
    mock_agent.run = mock_agent_run
    monkeypatch.setattr("app.agent.get_main_agent", lambda *args, **kwargs: mock_agent)
    deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.run_agent("prompt", deps)
    assert result.response.response == "An unexpected error occurred"


@pytest.mark.asyncio
async def test_run_complete_agent_success(monkeypatch):
    """Test run_complete_agent successfully completes a score."""
    score = Score(title="test", composer="test")
    mock_result = MagicMock()
    mock_result.output = score
    mock_agent_run = AsyncMock(return_value=mock_result)
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    result = await agent.run_complete_agent(score)
    assert result == score


@pytest.mark.asyncio
async def test_run_complete_agent_http_error_429(monkeypatch):
    """Test run_complete_agent with a 429 HTTP error."""
    mock_agent_run = AsyncMock(side_effect=ModelHTTPError(429, "error"))
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    score = Score(title="test", composer="test")
    result = await agent.run_complete_agent(score)
    assert result == score


@pytest.mark.asyncio
async def test_run_complete_agent_http_error_other(monkeypatch):
    """Test run_complete_agent with a non-429 HTTP error."""
    mock_agent_run = AsyncMock(side_effect=ModelHTTPError(500, "error"))
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    score = Score(title="test", composer="test")
    result = await agent.run_complete_agent(score)
    assert result == score


@pytest.mark.asyncio
async def test_run_complete_agent_exception(monkeypatch):
    """Test run_complete_agent with a generic exception."""
    mock_agent_run = AsyncMock(side_effect=Exception("error"))
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    score = Score(title="test", composer="test")
    result = await agent.run_complete_agent(score)
    assert result == score


@pytest.mark.asyncio
async def test_run_imslp_agent_success(monkeypatch):
    """Test run_imslp_agent success path."""

    mock_result = MagicMock()
    mock_result.output = ImslpResponse(response="success", score_ids=[1])
    mock_result.all_messages.return_value = []
    mock_agent_run = AsyncMock(return_value=mock_result)
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    monkeypatch.setattr("app.agent.Agent", MagicMock(return_value=mock_agent_instance))

    result = await agent.run_imslp_agent("prompt")
    assert result.response.response == "success"
    assert result.response.score_ids == [1]


@pytest.mark.asyncio
async def test_run_imslp_agent_history_parsing(monkeypatch):
    """Test message history parsing in run_imslp_agent."""

    mock_result = MagicMock()
    mock_result.output = ImslpResponse(response="success", score_ids=[])
    mock_result.all_messages.return_value = []
    mock_agent_run = AsyncMock(return_value=mock_result)
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    monkeypatch.setattr("app.agent.Agent", MagicMock(return_value=mock_agent_instance))

    # Invalid history triggers except block and defaults to None
    await agent.run_imslp_agent("prompt", message_history="invalid_history")
    mock_agent_run.assert_called_with(
        "<user_request>\nprompt\n</user_request>", message_history=None
    )


@pytest.mark.asyncio
async def test_run_agent_history_parsing(monkeypatch):
    """Test message history parsing in run_agent."""

    mock_result = MagicMock()
    mock_result.output = Response(response="success")
    mock_result.all_messages.return_value = []
    mock_agent_run = AsyncMock(return_value=mock_result)
    mock_agent = MagicMock()
    mock_agent.run = mock_agent_run
    monkeypatch.setattr("app.agent.get_main_agent", lambda *args, **kwargs: mock_agent)

    deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    # Invalid history triggers except block and defaults to None
    await agent.run_agent("prompt", deps, message_history="invalid_history")
    mock_agent_run.assert_called_with(
        "<user_request>\nprompt\n</user_request>", message_history=None, deps=deps
    )


@pytest.mark.asyncio
async def test_run_imslp_complete_agent_success(monkeypatch):
    """Test run_imslp_complete_agent successfully completes an entry."""
    score_base = ScoreBase(title="test", composer="test")
    mock_result = MagicMock()
    mock_result.output = score_base
    mock_agent_run = AsyncMock(return_value=mock_result)
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)

    result = await agent.run_imslp_complete_agent('{"title": "test"}')
    assert result == score_base


@pytest.mark.asyncio
async def test_run_imslp_complete_agent_http_error_retry(monkeypatch):
    """Test run_imslp_complete_agent retries on 503 error."""
    score_base = ScoreBase(title="test", composer="test")
    mock_result = MagicMock()
    mock_result.output = score_base
    mock_agent_run = AsyncMock(side_effect=[ModelHTTPError(503, "error"), mock_result])
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    monkeypatch.setattr("app.agent.time.sleep", lambda x: None)

    result = await agent.run_imslp_complete_agent('{"title": "test"}')
    assert result == score_base
    assert mock_agent_run.call_count == 2


@pytest.mark.asyncio
async def test_run_imslp_complete_agent_http_error_no_retry(monkeypatch):
    """Test run_imslp_complete_agent does not retry on 4xx error."""
    mock_agent_run = AsyncMock(side_effect=ModelHTTPError(400, "error"))
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)

    with pytest.raises(ModelHTTPError):
        await agent.run_imslp_complete_agent('{"title": "test"}')
    assert mock_agent_run.call_count == 1


@pytest.mark.asyncio
async def test_run_imslp_complete_agent_generic_exception(monkeypatch):
    """Test run_imslp_complete_agent raises after max retries."""
    mock_agent_run = AsyncMock(side_effect=Exception("error"))
    mock_agent_instance = MagicMock()
    mock_agent_instance.run = mock_agent_run
    mock_agent_class = MagicMock(return_value=mock_agent_instance)
    monkeypatch.setattr("app.agent.Agent", mock_agent_class)
    monkeypatch.setattr("app.agent.time.sleep", lambda x: None)

    with pytest.raises(Exception):
        await agent.run_imslp_complete_agent('{"title": "test"}')
    assert mock_agent_run.call_count == 5
