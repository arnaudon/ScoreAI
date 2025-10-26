from typing import List

import numpy as np
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from shared_models.responses import FullResponse, Response
from shared_models.score_models import Score, Scores

load_dotenv()


provider = GoogleProvider()
model = GoogleModel("gemini-2.5-flash-lite", provider=provider)
agent = Agent(
    model,
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
    return f"The scores infos are {ctx.deps.model_dump_json()}."


from pydantic import BaseModel


class TitleFilter(BaseModel):
    composer: str


@agent.tool
async def get_random_score_by_composer(ctx: RunContext[Scores], filter_params: TitleFilter) -> str:
    scores = []
    for score in ctx.deps.scores:
        if score.composer.lower() == filter_params.composer.lower():
            scores.append(score)
    if scores:
        return np.random.choice(scores).model_dump_json()
    return "Not found"


async def run_agent(prompt: str, deps: Scores, message_history=None):
    res = await agent.run(
        prompt,
        message_history=message_history,
        deps=deps,
    )
    return FullResponse(response=res.output, message_history=res.all_messages())


if __name__ == "__main__":
    import asyncio

    async def main():
        res = await run_agent("Write a haiku about code.")
        print(res)

    asyncio.run(main())
