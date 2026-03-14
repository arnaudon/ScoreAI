"""add short_description_fr and long_description_fr

Revision ID: 4a2b2b8b97b4
Revises: 6df28f7fbc33
Create Date: 2024-03-14 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "4a2b2b8b97b4"
down_revision: Union[str, None] = "6df28f7fbc33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "score",
        sa.Column("short_description_fr", AutoString(), nullable=False, server_default=""),
    )
    op.add_column(
        "score",
        sa.Column("long_description_fr", AutoString(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("score", "long_description_fr")
    op.drop_column("score", "short_description_fr")
