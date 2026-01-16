"""add role

Revision ID: 8662fe315087
Revises: a446b5001994
Create Date: 2026-01-15 14:57:04.285162

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlmodel.sql.sqltypes import AutoString

# revision identifiers, used by Alembic.
revision: str = "8662fe315087"
down_revision: Union[str, Sequence[str], None] = "a446b5001994"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user",
        sa.Column("role", AutoString(), nullable=False, server_default="user"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user", "role")
