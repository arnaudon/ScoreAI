"""Backend main entry point."""

import json
import os
from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator

from fastapi import Depends, FastAPI
from shared.scores import Score, Scores
from sqlmodel import Session, select

import app.users as users
from app.agent import run_agent
from app.db import get_session, init_db

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, tags=["users"])


@app.post("/scores")
def add_score(score: Score, session: Session = Depends(get_session)):
    """Add a score to the db."""
    session.add(score)
    session.commit()
    session.refresh(score)
    return score


@app.delete("/scores/{score_id}")
def delete_score(score_id: int, session: Session = Depends(get_session)):
    """Delete a score from the db."""
    score = session.get(Score, score_id)
    if score is not None:
        try:
            os.remove(score.pdf_path)
        except FileNotFoundError:
            pass
        session.delete(score)
    session.commit()


@app.post("/scores/{score_id}/play")
def add_play(score_id: int, session: Session = Depends(get_session)):
    """Add a play to the db."""
    score = session.get(Score, score_id)
    if score is not None:
        score.number_of_plays += 1
        session.commit()
        session.refresh(score)
    return score


@app.get("/scores")
def get_scores(session: Session = Depends(get_session)):
    """Get all scores from the db."""
    return session.exec(select(Score)).all()


@app.post("/agent")
async def run(prompt: str, deps: str, message_history=None):  # pragma: no cover
    """Run the agent."""
    return await run_agent(prompt, message_history=message_history, deps=Scores(**json.loads(deps)))
