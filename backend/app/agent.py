"""LLM agent module."""

import os
import random
from typing import Any

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.mcp import MCPServerSSE

from shared import FullResponse, Response, Score, Scores, User
from shared.scores import Difficulty

logfire.configure()
logfire.instrument_pydantic_ai()

load_dotenv()

MODEL: Any = os.getenv("MODEL", "google-gla:gemini-2.5-flash-lite")
postgres_server = MCPServerSSE("http://mcp-postgres:8001/sse")


_difficulty_map = {
    Difficulty.easy.name: 0,
    Difficulty.moderate.name: 1,
    Difficulty.intermediate.name: 2,
    Difficulty.advanced.name: 3,
    Difficulty.expert.name: 4,
}


class Filter(BaseModel):
    """Specifies filtering criteria for selecting musical scores."""

    composer: str


class Deps(BaseModel):
    """Defines dependencies to be injected into the agent's context."""

    user: User
    scores: Scores


def get_main_agent():
    """Initializes and returns the main agent for handling user queries about scores."""
    agent = Agent(
        MODEL,
        output_type=Response,
        deps_type=Deps,
        system_prompt="""Your task it to find a score to play.
        Write score id entry into score_id.
        If multiple scores are possible, return None for the score_id.
        If one score is available, write score_id.
        Do not mention score_id in your response.
        If multiple choices are possible, list them without id.
        Use my username in the conversations.
        """,
        toolsets=[postgres_server],
    )

    @agent.tool
    async def get_score_info(ctx: RunContext[Deps]) -> str:
        """Retrieves a JSON string with information about available musical scores."""
        return f"The scores infos are {ctx.deps.scores.model_dump_json()}."

    @agent.tool
    async def get_user_name(ctx: RunContext[Deps]) -> str:
        """Retrieves the current user's name from the context."""
        return ctx.deps.user.username

    @agent.tool
    async def get_random_score_by_composer(
        ctx: RunContext[Deps], filter_params: Filter
    ) -> str:
        """Selects and returns a random score by a specific composer."""
        scores = []
        for score in ctx.deps.scores.scores:
            if score.composer.lower() == filter_params.composer.lower():
                scores.append(score)
        if scores:
            return random.choice(scores).model_dump_json()
        return "Not found"

    @agent.tool
    async def get_easiest_score_by_composer(
        ctx: RunContext[Deps], filter_params: Filter
    ) -> str:
        """
        Finds the easiest score by a given composer.

        If multiple scores share the minimum difficulty, one is chosen at random.
        """
        scores = []
        for score in ctx.deps.scores.scores:
            if filter_params.composer.lower() in score.composer.lower():
                scores.append(score)
        if scores:
            difficulties = [_difficulty_map[score.difficulty] for score in scores]
            easy_scores = [
                s for d, s in zip(difficulties, scores) if d == min(difficulties)
            ]
            return random.choice(easy_scores).model_dump_json()
        return "Not found"

    return agent


async def run_imslp_agent(prompt: str, message_history=None):
    """
    Run an agent specialized for querying the IMSLP database.

    This agent acts as a database assistant for the public.imslp table,
    translating natural language prompts into SQL queries.

    Args:
        prompt: The user's query about the IMSLP database.
        message_history: The previous messages in the conversation.

    Returns:
        A FullResponse object containing the agent's response and message history.
    """
    agent = Agent(
        MODEL,
        system_prompt="""
        You are a database assistant. 
        Your ONLY source of data is the table: public.imslp.
        If you are unsure, ALWAYS assume the user is talking about public.imslp.
        Never ask the user for a table name; always use the one provided here.
        When asked about a score, consider it as an entry.
        The column instrumentation works for instrument, with case unsensitive search.
        When asked about time for scores, use the column year.
        You are also a SQL expert for PostgreSQL. 
        CRITICAL: Always use single quotes (') for string literals in SQL queries.
        Example: WHERE instrumentation LIKE '%piano%'
        NEVER use double quotes (") for strings.
        """,
        toolsets=[postgres_server],
        output_type=Scores,
        retries=3,
    )

    try:
        res = await agent.run(
            prompt,
            message_history=message_history,
        )
        response = Response(response=res.output.model_dump_json(), score_id=0)
        history = res.all_messages()
    except ModelHTTPError as e:
        history = []
        if e.status_code == 429:
            response = Response(response="Rate limit exceeded (Quota hit)")
        else:
            response = Response(response="An HTTP error occurred")
    except Exception:  # pylint: disable=broad-exception-caught
        history = []
        response = Response(response="An unexpected error occurred")

    return FullResponse(response=response, message_history=history)


async def run_agent(prompt: str, deps: Deps, message_history=None):
    """
    Run the main conversational agent to find musical scores.

    Args:
        prompt: The user's message to the agent.
        deps: The dependencies (user and scores data) for the agent.
        message_history: The previous messages in the conversation.

    Returns:
        A FullResponse object containing the agent's response and message history.
    """
    agent = get_main_agent()
    try:
        res = await agent.run(
            prompt,
            message_history=message_history,
            deps=deps,
        )
        response = res.output
        history = res.all_messages()
    except ModelHTTPError as e:
        history = []
        if e.status_code == 429:
            response = Response(response="Rate limit exceeded (Quota hit)")
        else:
            response = Response(response="An HTTP error occurred")
    except Exception:  # pylint: disable=broad-exception-caught
        history = []
        response = Response(response="An unexpected error occurred")

    return FullResponse(response=response, message_history=history)


async def run_complete_agent(score: Score):
    """
    Run an agent to find and add missing information to a score.

    This agent uses a search tool to enrich a Score object with details
    like year, instrumentation, etc.

    Args:
        score: The Score object with potentially missing information.

    Returns:
        The updated Score object.
    """
    agent = Agent(
        MODEL,
        output_type=Score,
        system_prompt="""You are a music expert, and your task it to provide accurate
        informations about a music piece. Use the search tool to find current information
        if you don't know the answer. Ignore pdf_path, user_id, id and number_of_play.
        """,
        retries=5,
        tools=[duckduckgo_search_tool()],
    )
    prompt = f"Find the information about music piece {score.title} composed by {score.composer}."
    try:
        res = await agent.run(prompt)
        response = res.output
    except ModelHTTPError as e:
        if e.status_code == 429:
            response = score
        else:
            response = score
    except Exception:  # pylint: disable=broad-exception-caught
        response = score
    return response
