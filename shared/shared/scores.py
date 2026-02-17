"""Score models."""

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from shared import User


class Difficulty(str, Enum):
    """Difficulty levels."""

    easy = "easy"
    moderate = "moderate"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class Period(str, Enum):
    """Periods of music history."""

    Medieval = "Medieval"
    Renaissance = "Renaissance"
    Baroque = "Baroque"
    Classical = "Classical"
    Romantic = "Romantic"
    Modernist = "Modernist"
    Postmodernist = "Postmodernist"


class ScoreBase(BaseModel):
    """Score base model."""

    title: str = Field()
    composer: str = Field()
    year: int = Field(default=1750, gt=500)
    period: Period = Field(default=Period.Classical)
    # https://en.wikipedia.org/wiki/List_of_classical_music_genres
    genre: str = Field(default="Classical")
    form: str = Field(default="Sonata")  # https://en.wikipedia.org/wiki/Musical_form
    short_description: str = Field(default="")
    long_description: str = Field(default="")
    youtube_url: str = Field(default="")
    difficulty: Difficulty = Field(default=Difficulty.moderate)
    notable_interpreters: str = Field(default="")


class Score(ScoreBase, table=True):
    """Score table"""

    __tablename__ = "score"  # type: ignore[reportAssignmentType]
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    # internal data
    pdf_path: str = Field(default="")
    number_of_plays: int = 0
    source: str = Field(default="IMSLP")
    imslp_id: int | None = Field(default=None)
    user_id: int | None = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="scores")


class Scores(BaseModel):
    """Scores table"""

    scores: List[Score]

    def __len__(self):
        return len(self.scores)


class IMSLP(ScoreBase, table=True):
    """IMSL score model."""

    id: int | None = Field(default=None, primary_key=True)
    permlink: str = Field()
    score_metadata: str = Field(default="")
    pdf_urls: str = Field(default="")
