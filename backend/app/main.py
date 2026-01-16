"""Backend main entry point."""

import json
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Annotated, AsyncGenerator

from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from app import users
from app.agent import Deps, run_agent
from app.db import get_session, init_db
from app.users import get_admin_user, get_current_user
from shared import Score, Scores, User

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, tags=["users"])


@app.post("/scores")
def add_score(
    score: Score,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Add a score to the db."""
    score.user_id = current_user.id
    session.add(score)
    session.commit()
    session.refresh(score)
    return score


@app.delete("/scores/{score_id}")
def delete_score(
    score_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Delete a score from the db."""
    score = session.exec(
        select(Score).where(Score.id == score_id, Score.user_id == current_user.id)
    ).first()
    if score is not None:
        session.delete(score)
    session.commit()


@app.post("/scores/{score_id}/play")
def add_play(
    score_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Add a play to the db."""
    score = session.exec(
        select(Score).where(Score.id == score_id, Score.user_id == current_user.id)
    ).first()
    if score is not None:
        score.number_of_plays += 1
        session.commit()
        session.refresh(score)
    return score


@app.get("/scores")
def get_scores(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Get all scores from the db."""
    return session.exec(select(Score).where(Score.user_id == current_user.id)).all()


@app.post("/agent")
async def run(
    prompt: str,
    deps: str,
    current_user: Annotated[User, Depends(get_current_user)],
    message_history=None,
):  # pragma: no cover
    """Run the agent."""
    return await run_agent(
        prompt,
        message_history=message_history,
        deps=Deps(user=current_user, scores=Scores(**json.loads(deps))),
    )
