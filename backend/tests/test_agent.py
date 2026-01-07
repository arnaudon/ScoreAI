"""test backend agnent.py"""

from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.models.test import TestModel
from shared.responses import FullResponse, Response
from shared.scores import Scores

from app import agent


async def test_agent_success(test_scores: Scores):
    """test agent happy path with TestModel"""
    agent.MODEL = TestModel()
    result = await agent.run_agent(prompt="test", deps=test_scores)
    assert isinstance(result, FullResponse)


async def test_agent_http_error(monkeypatch, test_scores: Scores):
    """run_agent returns helpful message on ModelHTTPError (covers 429/other)."""

    class DummyRes:
        def __init__(self, output: Response):
            self.output = output

        def all_messages(self):  # pragma: no cover - trivial
            return []

    async def failing_run_429(*args, **kwargs):
        raise ModelHTTPError("url", 429, "Too Many Requests")

    async def failing_run_other(*args, **kwargs):
        raise ModelHTTPError("url", 500, "Server Error")

    # First cover 429 branch
    AgentCls = agent.get_agent().__class__

    async def run_with_429(prompt, message_history=None, deps=None):
        raise ModelHTTPError("url", 429, "Too Many Requests")

    async def run_with_500(prompt, message_history=None, deps=None):
        raise ModelHTTPError("url", 500, "Server Error")

    # monkeypatch get_agent to return an object whose run raises 429
    class FakeAgent:
        async def run(self, *_, **__):
            raise ModelHTTPError("url", 429, "Too Many Requests")

    class FakeAgent500:
        async def run(self, *_, **__):
            raise ModelHTTPError("url", 500, "Server Error")

    monkeypatch.setattr(agent, "get_agent", lambda: FakeAgent())
    result_429 = await agent.run_agent("test", deps=test_scores)
    assert isinstance(result_429.response, Response)

    # now cover generic HTTP error branch
    monkeypatch.setattr(agent, "get_agent", lambda: FakeAgent500())
    result_other = await agent.run_agent("test", deps=test_scores)
    assert isinstance(result_other.response, Response)


async def test_agent_generic_exception(monkeypatch, test_scores: Scores):
    """run_agent handles unexpected exceptions gracefully."""

    class FakeAgent:
        async def run(self, *_, **__):
            raise RuntimeError("boom")

    monkeypatch.setattr(agent, "get_agent", lambda: FakeAgent())
    result = await agent.run_agent("test", deps=test_scores)
    assert isinstance(result.response, Response)
    assert "unexpected error" in result.response.response
