"""User models."""

from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from shared.scores import Score


class User(SQLModel, table=True):
    """User model."""

    __tablename__ = "user"  # type: ignore[reportAssignmentType]
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None
    scores: List["Score"] = Relationship(back_populates="user")
