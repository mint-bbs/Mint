"""thread_rank

Revision ID: af881b915a02
Revises: 91739fb7275b
Create Date: 2024-11-10 16:34:27.017491

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "af881b915a02"
down_revision: Union[str, None] = "91739fb7275b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "threads",
        sa.Column(
            "last_wrote_at",
            sa.DateTime(timezone=True),
            default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("threads", "last_wrote_at")
