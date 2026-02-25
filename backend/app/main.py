"""Backend main entry point."""

import json
from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path
from typing import Annotated, AsyncGenerator

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from app import imslp, users
from app.agent import Deps, run_agent, run_complete_agent, run_imslp_agent
from app.db import get_session, init_db
from app.file_helper import file_helper
from app.users import get_current_user, get_current_user_from_token
from shared.scores import Score, Scores
from shared.user import User

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
# mount PDF.js for pdf rendering
current_file = Path(__file__).resolve()
app.mount("/pdfjs", StaticFiles(directory=current_file.parent / "pdfjs"), name="pdfjs")

app.include_router(users.router, tags=["users"])
app.include_router(imslp.router, tags=["imslp"])


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


@app.post("/complete_score", dependencies=[Depends(get_current_user)])
async def complete_score(score: Score):  # pragma: no cover
    """Complete a score."""
    return await run_complete_agent(score)


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


@app.post("/imslp_agent")
async def run_imslp_agent_api(
    prompt: str,
    current_user: Annotated[User, Depends(get_current_user)],
    message_history=None,
):  # pragma: no cover
    """Run the imslp agent."""
    return await run_imslp_agent(prompt, message_history=message_history)


@app.post("/agent")
async def run_main_agent(
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


def get_pdf_user(token: str = ""):  # pragma: no cover
    """Dependency for PDF endpoints - accepts token as query param."""
    return get_current_user_from_token(token)


@app.get("/pdf/{filename}")
def get_pdf(filename: str, _user=Depends(get_pdf_user)):
    """Get the url of a pdf file."""
    obj = file_helper.download_pdf(filename)
    return StreamingResponse(obj["Body"], media_type="application/pdf")


@app.post("/pdf", dependencies=[Depends(get_current_user)])
def upload_pdf(file: UploadFile = File(...)):
    """Upload a pdf file."""
    if file.content_type != "application/pdf":  # pragma: no cover
        raise HTTPException(status_code=400, detail="Only PDFs allowed")
    try:
        file_helper.upload_pdf(file.filename, file.file)
        return {"message": "Upload successful", "file_id": file.filename}

    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/pdf/{filename}", dependencies=[Depends(get_current_user)])
def delete_pdf(filename: str):
    """Delete a pdf file."""
    file_helper.delete_pdf(filename)
    return {"message": "Delete successful"}
