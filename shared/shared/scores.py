"""Score models."""

from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from shared.user import User


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


class ScoreBase(SQLModel):
    """Score base model."""

    title: str = Field()
    composer: str = Field()
    year: int = Field(default=1750, gt=-1000)
    period: Period = Field(default=Period.Classical)
    genre: str = Field(default="Classical")
    form: str = Field(default="Sonata")
    style: str = Field(default="")
    key: str = Field(default="")
    instrumentation: str = Field(default="")


class Score(ScoreBase, table=True):
    """Score table"""

    __tablename__ = "score"  # type: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    pdf_path: str = Field(default="")
    number_of_plays: int = 0
    source: str = Field(default="IMSLP")
    imslp_id: int | None = Field(default=None)
    user_id: int | None = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="scores")

    short_description: str = Field(default="")
    short_description_fr: str = Field(default="")
    long_description: str = Field(default="")
    long_description_fr: str = Field(default="")
    youtube_url: str = Field(default="")
    difficulty: Difficulty = Field(default=Difficulty.moderate)
    notable_interpreters: str = Field(default="")


class Scores(BaseModel):
    """Scores table"""

    scores: List[Score]

    def __len__(self):
        return len(self.scores)


class ScoreCreate(ScoreBase):
    """Request body for creating a score.

    Excludes server-owned fields (``id``, ``user_id``, ``number_of_plays``) so
    clients cannot set them. Extra fields from the client are silently dropped
    by pydantic's default behavior.
    """

    pdf_path: str = Field(default="")
    source: str = Field(default="IMSLP")
    imslp_id: int | None = Field(default=None)
    short_description: str = Field(default="")
    short_description_fr: str = Field(default="")
    long_description: str = Field(default="")
    long_description_fr: str = Field(default="")
    youtube_url: str = Field(default="")
    difficulty: Difficulty = Field(default=Difficulty.moderate)
    notable_interpreters: str = Field(default="")


class ScoreUpdate(BaseModel):
    """Partial update body. All fields optional; server-owned fields absent."""

    title: str | None = None
    composer: str | None = None
    year: int | None = None
    period: Period | None = None
    genre: str | None = None
    form: str | None = None
    style: str | None = None
    key: str | None = None
    instrumentation: str | None = None
    pdf_path: str | None = None
    source: str | None = None
    imslp_id: int | None = None
    short_description: str | None = None
    short_description_fr: str | None = None
    long_description: str | None = None
    long_description_fr: str | None = None
    youtube_url: str | None = None
    difficulty: Difficulty | None = None
    notable_interpreters: str | None = None


class IMSLP(ScoreBase, table=True):
    """IMSL score model."""

    id: int | None = Field(default=None, primary_key=True)
    permlink: str = Field()
    score_metadata: str = Field(default="")
    pdf_urls: str = Field(default="")


class IMSLPScores(BaseModel):
    """IMLSP scores table"""

    scores: List[IMSLP]

    def __len__(self):
        return len(self.scores)  # pragma: no cover
