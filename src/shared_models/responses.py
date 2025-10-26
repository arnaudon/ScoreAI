from typing import List, Optional

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage


class Response(BaseModel):
    response: str
    follow_up_required: bool
    score_id: Optional[int]


class FullResponse(BaseModel):
    response: Response
    message_history: List[ModelMessage]
