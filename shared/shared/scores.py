"""Score models."""

from enum import Enum
from datetime import date

from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from shared import User


class Difficulty(Enum):
    """Difficulty levels."""

    easy = "easy"
    moderate = "moderate"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class Period(Enum):
    """Periods of music history."""

    Medieval = "Medieval"
    Renaissance = "Renaissance"
    Baroque = "Baroque"
    Classical = "Classical"
    Romantic = "Romantic"
    Modernist = "Modernist"
    Postmodernist = "Postmodernist"


class DataScore(BaseModel):
    title: str = Field()
    composer: str = Field()


class Score(SQLModel, table=True):
    """Score model"""

    __tablename__ = "score"  # type: ignore[reportAssignmentType]
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)

    # score data
    title: str = Field()
    composer: str = Field()
    year: int = Field(gt=0, lt=date.today().year)
    period: Period = Field()
    genre: str = Field()  # https://en.wikipedia.org/wiki/List_of_classical_music_genres
    form: str = Field()  # https://en.wikipedia.org/wiki/Musical_form
    short_description: str = Field()
    long_description: str = Field()
    youtube_url: str = Field()
    difficulty: Difficulty = Field()
    notable_interpreters: str = Field()

    # internal data
    pdf_path: str = Field()
    number_of_plays: int = 0
    user_id: int | None = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="scores")


class Scores(BaseModel):
    """Scores table"""

    scores: List[Score]

    def __len__(self):
        return len(self.scores)
