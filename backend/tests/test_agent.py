"""test backend agnent.py"""

from pydantic_ai.models.test import TestModel
from shared.responses import FullResponse
from shared.scores import Scores

from app import agent


async def test_agent(test_scores: Scores):
    """test agent"""
    agent.MODEL = TestModel()
    result = await agent.run_agent(prompt="test", deps=test_scores)
    assert isinstance(result, FullResponse)
