"""create responses table

Revision ID: d4b120debf5d
Revises: e5b09da894a1
Create Date: 2024-10-15 20:23:05.035031

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4b120debf5d"
down_revision: Union[str, None] = "e5b09da894a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "responses",
        sa.Column("id", sa.String(10), primary_key=True),
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("board", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("content", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("responses")
