"""Backend main entry point."""

import json

from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from backend.agent import run_agent
from backend.db import get_session, init_db
from shared_models.scores import Score, Scores

app = FastAPI()


@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    init_db()


@app.post("/scores")
def add_score(score: Score, session: Session = Depends(get_session)):
    """Add a score to the db."""
    session.add(score)
    session.commit()
    session.refresh(score)
    return score


@app.get("/scores")
def get_scores(session: Session = Depends(get_session)):
    """Get all scores from the db."""
    return session.exec(select(Score)).all()


@app.post("/agent")
async def run(prompt: str, deps: str, message_history=None):
    """Run the agent."""
    return await run_agent(prompt, message_history=message_history, deps=Scores(**json.loads(deps)))
