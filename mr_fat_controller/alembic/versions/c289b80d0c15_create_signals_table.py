# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Create the signals table.

Revision ID: c289b80d0c15
Revises: 65f463b84705
Create Date: 2025-01-26 20:18:40.850374

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer

# revision identifiers, used by Alembic.
revision = "c289b80d0c15"
down_revision = "65f463b84705"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the signals table."""
    op.create_table(
        "signals",
        Column("id", Integer, primary_key=True),
        Column("entity_id", Integer, ForeignKey("entities.id")),
    )


def downgrade() -> None:
    """Drop the signals table."""
    op.drop_table("signals")
