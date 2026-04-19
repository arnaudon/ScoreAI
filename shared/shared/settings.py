"""Settings models."""

from sqlmodel import Field, SQLModel


class Setting(SQLModel, table=True):
    """Key-value settings for the app."""

    key: str = Field(primary_key=True)
    value: str
