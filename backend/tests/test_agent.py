"""Tests for the agent module."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.test import TestModel

from app import agent
from shared.responses import FullResponse
from shared.scores import Score, Scores
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
async def test_get_random_score_by_composer_not_found():
    """Test get_random_score_by_composer when no score is found."""
    ctx = MagicMock()
    ctx.deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.get_random_score_by_composer(
        ctx, agent.Filter(composer="Unknown")
    )
    assert result == "Not found"


@pytest.mark.asyncio
async def test_get_easiest_score_by_composer_not_found():
    """Test get_easiest_score_by_composer when no score is found."""
    ctx = MagicMock()
    ctx.deps = agent.Deps(user=User(username="test"), scores=Scores(scores=[]))
    result = await agent.get_easiest_score_by_composer(
        ctx, agent.Filter(composer="Unknown")
    )
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
    mock_agent_run = AsyncMock(side_effect=ModelHTTPError(500, "error"))
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
    mock_agent_run = AsyncMock(side_effect=ModelHTTPError(500, "error"))
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
