"""
Extended agent.py test coverage, especially for error handling and edge cases.
"""

from unittest import mock

import pytest

from app import agent
from shared.responses import FullResponse
from shared.scores import Score


class DummyExc(Exception):
    """Dummy exception for testing."""


@pytest.mark.anyio
async def test_run_agent_model_http_error(monkeypatch, test_scores, test_user):
    """
    Test agent.ModelHTTPError handling, 429 and non-429.
    """

    # Subclass ModelHTTPError to ensure we match the except block in run_agent
    class MockModelHTTPError(agent.ModelHTTPError):
        """Mock ModelHTTPError."""

        def __init__(self, msg, status_code=500):
            # Bypass original init to avoid signature guessing issues
            Exception.__init__(self, msg)
            self.status_code = status_code

    async def raise_429(*a, **kw):  # pylint: disable=unused-argument
        raise MockModelHTTPError("Rate limit", status_code=429)

    async def raise_500(*a, **kw):  # pylint: disable=unused-argument
        raise MockModelHTTPError("HTTP error", status_code=500)

    dummy_agent = mock.Mock()
    dummy_agent.run = raise_429
    monkeypatch.setattr(agent, "get_main_agent", lambda: dummy_agent)
    result = await agent.run_agent("prompt", agent.Deps(user=test_user, scores=test_scores))
    assert isinstance(result, FullResponse)
    assert "Rate limit" in result.response.response
    # Repeat for other error
    dummy_agent.run = raise_500
    result2 = await agent.run_agent("prompt", agent.Deps(user=test_user, scores=test_scores))
    assert isinstance(result2, FullResponse)
    assert "HTTP error" in result2.response.response


@pytest.mark.anyio
async def test_run_agent_exception(monkeypatch, test_scores, test_user):
    """
    Test generic exception handler in run_agent.
    """

    async def fail(*a, **kw):  # pylint: disable=unused-argument
        raise Exception("oops")  # pylint: disable=broad-exception-raised

    dummy_agent = mock.Mock()
    dummy_agent.run = fail
    monkeypatch.setattr(agent, "get_main_agent", lambda: dummy_agent)
    result = await agent.run_agent("prompt", agent.Deps(user=test_user, scores=test_scores))
    assert isinstance(result, FullResponse)
    assert "unexpected error" in result.response.response.lower()


@pytest.mark.anyio
async def test_run_complete_agent_model_http_error(monkeypatch):  # pylint: disable=unused-argument
    """
    Test error handling in run_complete_agent.
    """

    # Patch Agent.run to raise ModelHTTPError(429)
    class DummyModelHTTPError(agent.ModelHTTPError):
        """Mock ModelHTTPError."""

        def __init__(self):
            Exception.__init__(self, "Rate limit")
            self.status_code = 429

    async def fail(*a, **kw):  # pylint: disable=unused-argument
        raise DummyModelHTTPError()

    monkeypatch.setattr(agent.Agent, "run", fail)
    score = Score(composer="Test", title="T", pdf_path="", user_id=1)
    out = await agent.run_complete_agent(score)
    assert isinstance(out, Score)
