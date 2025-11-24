"""test backend agnent.py"""

from pydantic_ai.models.test import TestModel

from scoreai.backend import agent
from scoreai.shared_models.responses import FullResponse
from scoreai.shared_models.scores import Scores


async def test_agent(test_scores: Scores):
    """test agent"""
    agent.MODEL = TestModel()
    result = await agent.run_agent(prompt="test", deps=test_scores)
    assert isinstance(result, FullResponse)
