"""initial migration

Revision ID: 6df28f7fbc33
Revises:
Create Date: 2026-03-13 14:10:35.479986

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlmodel.sql.sqltypes import AutoString

revision: str = "6df28f7fbc33"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial schema for user / score / imslp / setting.

    Columns added later are NOT here -- they come from subsequent migrations:
      * ``score.short_description_fr`` / ``score.long_description_fr`` -> 4a2b2b8b97b4
      * ``user.last_login`` -> 4a6222a48c48

    Existing deployments have ``alembic_version = '4a6222a48c48'`` so this
    script is a no-op for them; only fresh volumes run it.
    """
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", AutoString(), nullable=False),
        sa.Column("email", AutoString(), nullable=True),
        sa.Column("first_name", AutoString(), nullable=True),
        sa.Column("last_name", AutoString(), nullable=True),
        sa.Column("instrument", AutoString(), nullable=True),
        sa.Column("password", AutoString(), nullable=True),
        sa.Column("role", AutoString(), nullable=False, server_default="user"),
        sa.Column("credits", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("max_credits", sa.Integer(), nullable=False, server_default="50"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "score",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("composer", AutoString(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False, server_default="1750"),
        sa.Column("period", AutoString(), nullable=False, server_default="Classical"),
        sa.Column("genre", AutoString(), nullable=False, server_default="Classical"),
        sa.Column("form", AutoString(), nullable=False, server_default="Sonata"),
        sa.Column("style", AutoString(), nullable=False, server_default=""),
        sa.Column("key", AutoString(), nullable=False, server_default=""),
        sa.Column("instrumentation", AutoString(), nullable=False, server_default=""),
        sa.Column("pdf_path", AutoString(), nullable=False, server_default=""),
        sa.Column("number_of_plays", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source", AutoString(), nullable=False, server_default="IMSLP"),
        sa.Column("imslp_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("short_description", AutoString(), nullable=False, server_default=""),
        sa.Column("long_description", AutoString(), nullable=False, server_default=""),
        sa.Column("youtube_url", AutoString(), nullable=False, server_default=""),
        sa.Column("difficulty", AutoString(), nullable=False, server_default="moderate"),
        sa.Column("notable_interpreters", AutoString(), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "imslp",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", AutoString(), nullable=False),
        sa.Column("composer", AutoString(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False, server_default="1750"),
        sa.Column("period", AutoString(), nullable=False, server_default="Classical"),
        sa.Column("genre", AutoString(), nullable=False, server_default="Classical"),
        sa.Column("form", AutoString(), nullable=False, server_default="Sonata"),
        sa.Column("style", AutoString(), nullable=False, server_default=""),
        sa.Column("key", AutoString(), nullable=False, server_default=""),
        sa.Column("instrumentation", AutoString(), nullable=False, server_default=""),
        sa.Column("permlink", AutoString(), nullable=False),
        sa.Column("score_metadata", AutoString(), nullable=False, server_default=""),
        sa.Column("pdf_urls", AutoString(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "setting",
        sa.Column("key", AutoString(), nullable=False),
        sa.Column("value", AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    """Drop everything. Only safe on fresh / non-prod databases."""
    op.drop_table("setting")
    op.drop_table("imslp")
    op.drop_table("score")
    op.drop_table("user")
