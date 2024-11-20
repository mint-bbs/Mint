"""ip_log

Revision ID: 72bf723f898e
Revises: af881b915a02
Create Date: 2024-11-20 16:42:54.169868

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "72bf723f898e"
down_revision: Union[str, None] = "af881b915a02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "threads",
        sa.Column("ipaddr", sa.String, nullable=True),
    )
    op.add_column(
        "responses",
        sa.Column("ipaddr", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("threads", "ipaddr")
    op.drop_column("responses", "ipaddr")
