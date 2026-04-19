"""Backend main entry point."""

import json
import logging
import os
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Annotated

import sentry_sdk
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app import config, imslp, users
from app.agent import Deps, run_agent, run_complete_agent, run_imslp_agent
from app.credits import consume_credit
from app.db import get_async_session, get_session
from app.file_helper import file_helper
from app.rate_limit import limiter
from app.users import get_admin_user, get_current_user, get_current_user_from_token
from shared.scores import Score, ScoreCreate, Scores, ScoreUpdate
from shared.settings import Setting
from shared.user import User

logger = getLogger(__name__)


def _init_sentry() -> None:
    """Opt-in Sentry init. No-op when SENTRY_DSN isn't set (dev / test / CI)."""
    if config.SENTRY_DSN:  # pragma: no cover
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            environment=config.SENTRY_ENVIRONMENT,
            traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
        )


_init_sentry()


class ChatRequest(BaseModel):
    """Shared body for agent chat endpoints."""

    prompt: str
    message_history: list | None = None


class MainAgentRequest(ChatRequest):
    """Body for /agent — adds a JSON-encoded ``Scores`` blob."""

    deps: str


class ModelsUpdate(BaseModel):
    """Body for POST /admin/model."""

    models: dict[str, str]


def configure_logging() -> None:
    """Configure root logger level/format from env. Idempotent."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    """Startup / shutdown events.

    Schema is owned by alembic (deploy.yaml and test_docker.yaml both run
    ``alembic upgrade head`` against the container), so the lifespan no
    longer calls ``init_db`` — doing so would race with the ALTER-based
    migrations on a fresh volume.
    """
    configure_logging()
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
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
        session.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=503, detail="database unreachable") from e
    return {"status": "ok"}


@app.post("/scores")
def add_score(
    score: ScoreCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Add a score to the db."""
    db_score = Score(**score.model_dump(), user_id=current_user.id)
    session.add(db_score)
    session.commit()
    session.refresh(db_score)
    return db_score


@app.post("/complete_score")
@limiter.limit(config.AGENT_RATE_LIMIT)
async def complete_score(
    request: Request,
    score: Score,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """Complete a score."""
    setting = await session.get(Setting, "model_complete")
    model = setting.value if setting else os.getenv("MODEL", "test")

    async with consume_credit(current_user.id, session):
        try:
            return await run_complete_agent(score, model)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e


@app.put("/scores/{score_id}")
def update_score(
    score_id: int,
    score_update: ScoreUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Update a score in the db."""
    db_score = session.exec(
        select(Score).where(Score.id == score_id, Score.user_id == current_user.id)
    ).first()

    if not db_score:
        raise HTTPException(status_code=404, detail="Score not found")

    for key, value in score_update.model_dump(exclude_unset=True).items():
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
@limiter.limit(config.AGENT_RATE_LIMIT)
async def run_imslp_agent_api(
    request: Request,
    body: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """Run the imslp agent."""
    setting = await session.get(Setting, "model_imslp")
    model = setting.value if setting else os.getenv("MODEL", "test")

    async with consume_credit(current_user.id, session):
        try:
            return await run_imslp_agent(
                body.prompt, message_history=body.message_history, model=model
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/agent")
@limiter.limit(config.AGENT_RATE_LIMIT)
async def run_main_agent(
    request: Request,
    body: MainAgentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_async_session),
):
    """Run the agent."""
    setting = await session.get(Setting, "model_main")
    model = setting.value if setting else os.getenv("MODEL", "test")

    async with consume_credit(current_user.id, session):
        try:
            return await run_agent(
                body.prompt,
                message_history=body.message_history,
                deps=Deps(user=current_user, scores=Scores(**json.loads(body.deps))),
                model=model,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e


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
def set_active_model(body: ModelsUpdate, session: Session = Depends(get_session)):
    """Set the currently active agent models."""
    for key, val in body.models.items():
        setting_key = f"model_{key}"
        setting = session.get(Setting, setting_key)
        if setting:
            setting.value = val
        else:
            setting = Setting(key=setting_key, value=val)
        session.add(setting)
    session.commit()
    return {"message": "Models updated", "models": body.models}


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
