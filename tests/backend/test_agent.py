"""test backend agnent.py"""

from pydantic_ai.models.test import TestModel

from scoreai.backend.agent import agent, run_agent
from scoreai.shared_models.responses import FullResponse
from scoreai.shared_models.scores import Scores


async def test_agent(test_scores: Scores):
    """test agent"""
    with agent.override(model=TestModel()):
        result = await run_agent(prompt="test", deps=test_scores)
    assert isinstance(result, FullResponse)
