"""LLM agent module."""

import os
import random

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from scoreai.shared_models.responses import FullResponse, Response
from scoreai.shared_models.scores import Scores

load_dotenv()

MODEL = os.getenv("MODEL", "google-gla:gemini-2.5-flash-lite")


class Filter(BaseModel):
    """Filter for random score tool."""

    composer: str


agent = Agent(
    MODEL,
    output_type=Response,
    deps_type=Scores,
    system_prompt="""Your task it to find a good score to play.
        Write score id entry into score_id.
        If multiple scores are possible, return None for the score_id.
        If one score is available, write score_id.
        Do not mention score_id in your response.
        If multiple choices are possible, list them without id.
        """,
)


@agent.tool
async def get_score_info(ctx: RunContext[Scores]) -> str:
    """Get score info."""
    return f"The scores infos are {ctx.deps.model_dump_json()}."


@agent.tool
async def get_random_score_by_composer(ctx: RunContext[Scores], filter_params: Filter) -> str:
    """Get a random score by composer."""
    scores = []
    for score in ctx.deps.scores:
        if score.composer.lower() == filter_params.composer.lower():
            scores.append(score)
    if scores:
        return random.choice(scores).model_dump_json()
    return "Not found"  # pragma: no cover


async def run_agent(prompt: str, deps: Scores, message_history=None):
    """Run the agent."""
    res = await agent.run(
        prompt,
        message_history=message_history,
        deps=deps,
    )
    return FullResponse(response=res.output, message_history=res.all_messages())
