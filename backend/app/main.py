"""Backend main entry point."""

import json
import os
import uuid
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Annotated, AsyncGenerator

from fastapi import Body, Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app import imslp, users
from app.agent import Deps, run_agent, run_complete_agent, run_imslp_agent
from app.db import get_async_session, get_session, init_db
from app.file_helper import file_helper
from app.rate_limit import limiter
from app.users import get_admin_user, get_current_user, get_current_user_from_token
from shared.scores import Score, Scores
from shared.settings import Setting
from shared.user import User

logger = getLogger(__name__)


def validate_prompt_security(prompt: str):
    """Validate the prompt against common injection attacks."""
    suspicious_keywords = [
        "ignore previous",
        "system prompt",
        "drop table",
        "bypass",
        "forget all instructions",
    ]
    if any(keyword in prompt.lower() for keyword in suspicious_keywords):
        raise HTTPException(status_code=400, detail="Invalid input detected.")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    """Placeholder for startup/shutdown events."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, tags=["users"])
app.include_router(imslp.router, tags=["imslp"])


@app.get("/health")
def health(session: Session = Depends(get_session)):
    """Liveness probe: returns 200 when the DB is reachable, 503 otherwise."""
    try:
        session.exec(text("SELECT 1"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise HTTPException(status_code=503, detail="database unreachable") from e
    return {"status": "ok"}


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


@app.post("/complete_score")
@limiter.limit("5/minute")
async def complete_score(
    request: Request,  # pylint: disable=unused-argument
    score: Score,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):  # pragma: no cover
    """Complete a score."""
    if current_user.credits <= 0:
        raise HTTPException(
            status_code=403,
            detail="You have run out of agent credits."
            "Please contact alexis.arnaudon@gmail.com to get more credits.",
        )

    async_user = await session.get(User, current_user.id)
    if async_user:
        async_user.credits -= 1
        session.add(async_user)
        await session.commit()

    setting = await session.get(Setting, "model_complete")
    model = setting.value if setting else os.getenv("MODEL", "test")

    try:
        result = await run_complete_agent(score, model)
    except Exception as e:
        async_user = await session.get(User, current_user.id)
        if async_user:
            async_user.credits += 1
            session.add(async_user)
            await session.commit()
        raise HTTPException(status_code=500, detail=str(e)) from e

    return result


@app.put("/scores/{score_id}")
def update_score(
    score_id: int,
    score_update: Score,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Update a score in the db."""
    db_score = session.exec(
        select(Score).where(Score.id == score_id, Score.user_id == current_user.id)
    ).first()

    if not db_score:
        raise HTTPException(status_code=404, detail="Score not found")

    score_data = score_update.model_dump(exclude_unset=True)
    for key, value in score_data.items():
        if key not in ("id", "user_id"):
            setattr(db_score, key, value)

    session.add(db_score)
    session.commit()
    session.refresh(db_score)
    return db_score


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
@limiter.limit("5/minute")
async def run_imslp_agent_api(
    request: Request,  # pylint: disable=unused-argument
    current_user: Annotated[User, Depends(get_current_user)],
    prompt: str = Body(...),
    message_history: list | None = Body(None),
    session: AsyncSession = Depends(get_async_session),
):  # pragma: no cover
    """Run the imslp agent."""
    validate_prompt_security(prompt)

    if current_user.credits <= 0:
        raise HTTPException(
            status_code=403,
            detail="You have run out of agent credits."
            "Please contact alexis.arnaudon@gmail.com to get more credits.",
        )

    async_user = await session.get(User, current_user.id)
    if async_user:
        async_user.credits -= 1
        session.add(async_user)
        await session.commit()

    setting = await session.get(Setting, "model_imslp")
    model = setting.value if setting else os.getenv("MODEL", "test")

    try:
        result = await run_imslp_agent(prompt, message_history=message_history, model=model)
    except Exception as e:
        async_user = await session.get(User, current_user.id)
        if async_user:
            async_user.credits += 1
            session.add(async_user)
            await session.commit()
        raise HTTPException(status_code=500, detail=str(e)) from e

    return result


@app.post("/agent")
@limiter.limit("5/minute")
async def run_main_agent(  # pylint: disable=too-many-positional-arguments
    request: Request,  # pylint: disable=unused-argument
    current_user: Annotated[User, Depends(get_current_user)],
    prompt: str = Body(...),
    deps: str = Body(...),
    message_history: list | None = Body(None),
    session: AsyncSession = Depends(get_async_session),
):  # pragma: no cover
    """Run the agent."""
    validate_prompt_security(prompt)

    if current_user.credits <= 0:
        raise HTTPException(
            status_code=403,
            detail="You have run out of agent credits."
            "Please contact alexis.arnaudon@gmail.com to get more credits.",
        )

    async_user = await session.get(User, current_user.id)
    if async_user:
        async_user.credits -= 1
        session.add(async_user)
        await session.commit()

    setting = await session.get(Setting, "model_main")
    model = setting.value if setting else os.getenv("MODEL", "test")

    try:
        result = await run_agent(
            prompt,
            message_history=message_history,
            deps=Deps(user=current_user, scores=Scores(**json.loads(deps))),
            model=model,
        )
    except Exception as e:
        async_user = await session.get(User, current_user.id)
        if async_user:
            async_user.credits += 1
            session.add(async_user)
            await session.commit()
        raise HTTPException(status_code=500, detail=str(e)) from e

    return result


@app.get("/admin/model", dependencies=[Depends(get_admin_user)])
def get_active_model(session: Session = Depends(get_session)):
    """Get the currently active agent models."""
    main_setting = session.get(Setting, "model_main")
    imslp_setting = session.get(Setting, "model_imslp")
    complete_setting = session.get(Setting, "model_complete")
    imslp_complete_setting = session.get(Setting, "model_imslp_complete")

    models = {
        "main": (main_setting.value if main_setting else os.getenv("MODEL", "test")),
        "imslp": (imslp_setting.value if imslp_setting else os.getenv("MODEL", "test")),
        "complete": (complete_setting.value if complete_setting else os.getenv("MODEL", "test")),
        "imslp_complete": (
            imslp_complete_setting.value if imslp_complete_setting else os.getenv("MODEL", "test")
        ),
    }
    return {"models": models}


@app.post("/admin/model", dependencies=[Depends(get_admin_user)])
def set_active_model(models: dict = Body(..., embed=True), session: Session = Depends(get_session)):
    """Set the currently active agent models."""
    for key, val in models.items():
        setting_key = f"model_{key}"
        setting = session.get(Setting, setting_key)
        if setting:
            setting.value = val
        else:
            setting = Setting(key=setting_key, value=val)
        session.add(setting)
    session.commit()
    return {"message": "Models updated", "models": models}


def get_pdf_user(token: str = "", session: Session = Depends(get_session)):  # pragma: no cover
    """Dependency for PDF endpoints - accepts token as query param."""
    return get_current_user_from_token(token, session)


@app.get("/pdf/{filename}")
def get_pdf(filename: str, _user=Depends(get_pdf_user)):
    """Get the url of a pdf file."""
    obj = file_helper.download_pdf(filename)
    return StreamingResponse(
        obj["Body"],
        media_type="application/pdf",
        headers={"Cache-Control": "public, max-age=86400, immutable"},
    )


@app.post("/pdf", dependencies=[Depends(get_current_user)])
def upload_pdf(file: UploadFile = File(...)):
    """Upload a pdf file."""
    if file.content_type != "application/pdf":  # pragma: no cover
        raise HTTPException(status_code=400, detail="Only PDFs allowed")
    try:
        file_id = f"{uuid.uuid4().hex}.pdf"
        file_helper.upload_pdf(file_id, file.file)
        return {"message": "Upload successful", "file_id": file_id}

    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/pdf/{filename}", dependencies=[Depends(get_current_user)])
def delete_pdf(filename: str):
    """Delete a pdf file."""
    file_helper.delete_pdf(filename)
    return {"message": "Delete successful"}
