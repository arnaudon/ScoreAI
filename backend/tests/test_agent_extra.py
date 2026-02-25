"""
Extended agent.py test coverage, especially for error handling and edge cases.
"""

import pytest
from unittest import mock
from pydantic_ai.models.test import TestModel
from app import agent
from shared.responses import FullResponse, Response
from shared.scores import Scores, Score
from shared.user import User


class DummyExc(Exception):
    pass


@pytest.mark.anyio
async def test_run_agent_ModelHTTPError(monkeypatch, test_scores, test_user):
    """
    Test agent.ModelHTTPError handling, 429 and non-429.
    """

    # Patch ModelHTTPError in agent module's namespace
    class PatchedModelHTTPError(Exception):
        def __init__(self, msg, status_code=500):
            super().__init__(msg)
            self.status_code = status_code

    monkeypatch.setattr(agent, "ModelHTTPError", PatchedModelHTTPError)

    async def raise_429(*a, **kw):
        raise agent.ModelHTTPError("429", status_code=429)

    async def raise_500(*a, **kw):
        raise agent.ModelHTTPError("500", status_code=500)

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
async def test_run_agent_Exception(monkeypatch, test_scores, test_user):
    """
    Test generic exception handler in run_agent.
    """

    async def fail(*a, **kw):
        raise Exception("oops")

    dummy_agent = mock.Mock()
    dummy_agent.run = fail
    monkeypatch.setattr(agent, "get_main_agent", lambda: dummy_agent)
    result = await agent.run_agent("prompt", agent.Deps(user=test_user, scores=test_scores))
    assert isinstance(result, FullResponse)
    assert "unexpected error" in result.response.response.lower()


@pytest.mark.anyio
async def test_run_complete_agent_ModelHTTPError(monkeypatch):
    """
    Test error handling in run_complete_agent.
    """

    # Patch Agent.run to raise ModelHTTPError(429)
    class DummyModelHTTPError(Exception):
        status_code = 429

    async def fail(*a, **kw):
        raise DummyModelHTTPError()

    agent.Agent.run = fail
    score = Score(composer="Test", title="T", pdf_path="", user_id=1)
    out = await agent.run_complete_agent(score)
    assert isinstance(out, Score)
