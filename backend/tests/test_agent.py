"""test backend agnent.py"""

from pydantic_ai.models.test import TestModel
from shared.responses import FullResponse
from shared.scores import Scores
from shared.user import User

from app import agent


async def test_agent_success(test_scores: Scores, test_user: User):
    """test agent happy path with TestModel"""
    agent.MODEL = TestModel()
    result = await agent.run_agent(
        prompt="test", deps=agent.Deps(user=test_user, scores=test_scores)
    )
    assert isinstance(result, FullResponse)
