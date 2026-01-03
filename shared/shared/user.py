from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None

