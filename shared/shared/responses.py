"""Response models."""

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage


class Response(BaseModel):
    """Response model."""

    response: str
    score_id: int | None = None
    score_ids: list[int] | None = None


class FullResponse(BaseModel):
    """Full response model with history."""

    response: Response
    message_history: list[ModelMessage]


class ImslpResponse(BaseModel):
    """Response model for IMSLP agent."""

    response: str
    score_ids: list[int]


class ImslpFullResponse(BaseModel):
    """Full response model with history for IMSLP agent."""

    response: ImslpResponse
    message_history: list[ModelMessage]
