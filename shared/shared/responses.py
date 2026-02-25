"""Response models."""

from typing import List, Optional

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage

from shared.scores import Scores


class Response(BaseModel):
    """Response model."""

    response: str
    score_id: Optional[int] = None


class FullResponse(BaseModel):
    """Full response model with history."""

    response: Response
    message_history: List[ModelMessage]


class ImslpResponse(BaseModel):
    """Response model for IMSLP agent."""

    response: str
    score_ids: List[int]


class ImslpFullResponse(BaseModel):
    """Full response model with history for IMSLP agent."""

    response: ImslpResponse
    message_history: List[ModelMessage]
