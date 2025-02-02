# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Link signals to points.

Revision ID: f11e0e87f8f6
Revises: c289b80d0c15
Create Date: 2025-01-26 21:39:16.571652

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer

# revision identifiers, used by Alembic.
revision = "f11e0e87f8f6"
down_revision = "c289b80d0c15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the necessary signal foreign key columns."""
    op.add_column("points", Column("through_signal_id", Integer, ForeignKey("signals.id"), nullable=True))
    op.add_column("points", Column("diverge_signal_id", Integer, ForeignKey("signals.id"), nullable=True))
    op.add_column("points", Column("root_signal_id", Integer, ForeignKey("signals.id"), nullable=True))


def downgrade() -> None:
    """Remove the signal foreign key columns."""
    op.drop_column("points", "through_signal_id")
    op.drop_column("points", "diverge_signal_id")
    op.drop_column("points", "root_signal_id")
