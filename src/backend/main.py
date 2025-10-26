import json

from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, select

from backend.agent import run_agent
from backend.db import get_session, init_db
from shared_models.score_models import Score, Scores

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/scores")
def add_score(score: Score, session: Session = Depends(get_session)):
    session.add(score)
    session.commit()
    session.refresh(score)
    return score


@app.get("/scores")
def get_scores(session: Session = Depends(get_session)):
    return session.exec(select(Score)).all()


@app.post("/agent")
async def run(prompt: str, deps: str, message_history=None):
    return await run_agent(prompt, message_history=message_history, deps=Scores(**json.loads(deps)))
