"""Score models."""

from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Score(SQLModel, table=True):
    """Score model"""

    id: int | None = Field(default=None, primary_key=True)
    pdf_path: str = Field()
    title: str = Field()
    composer: str = Field()
    number_of_plays: int = 0
    year: Optional[int] = None
    period: Optional[str] = None
    genre: Optional[str] = None


class Scores(BaseModel):
    """Scores table"""

    scores: List[Score]

    def __len__(self):
        return len(self.scores)
