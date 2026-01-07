"""Response models."""

from typing import List, Optional

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage


class Response(BaseModel):
    """Response model."""

    response: str
    score_id: Optional[int] = None


class FullResponse(BaseModel):
    """Full response model with history."""

    response: Response
    message_history: List[ModelMessage]
