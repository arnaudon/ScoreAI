"""Tests for the agent module."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.test import TestModel

from app import agent
from shared.responses import FullResponse
from shared.scores import Difficulty, Score, Scores
from shared.user import User


@pytest.mark.asyncio
async def test_agent_success(monkeypatch, test_scores: Scores, test_user: User):
    """test agent happy path with TestModel"""
    monkeypatch.setattr(agent, "MODEL", TestModel())
    result = await agent.run_agent(
        prompt="test", deps=agent.Deps(user=test_user, scores=test_scores)
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
    monkeypatch.setattr("app.agent.get_main_agent", lambda: mock_agent)
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
    monkeypatch.setattr("app.agent.get_main_agent", lambda: mock_agent)
    deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.run_agent("prompt", deps)
    assert result.response.response == "An HTTP error occurred"


@pytest.mark.asyncio
async def test_run_agent_exception(monkeypatch):
    """Test run_agent with a generic exception."""
    mock_agent_run = AsyncMock(side_effect=Exception("error"))
    mock_agent = MagicMock()
    mock_agent.run = mock_agent_run
    monkeypatch.setattr("app.agent.get_main_agent", lambda: mock_agent)
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
