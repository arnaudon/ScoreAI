"""test backend agnent.py"""

from pydantic_ai import Agent

from scoreai.backend.agent import run_agent
from scoreai.shared_models.responses import FullResponse
from scoreai.shared_models.scores import Scores


async def test_agent(agent: Agent, test_scores: Scores):
    """test agent"""
    result = await run_agent(prompt="test", deps=test_scores, agent=agent)
    assert isinstance(result, FullResponse)
