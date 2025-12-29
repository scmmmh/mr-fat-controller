"""Add device status columns.

Revision ID: 95651fc3abf7
Revises: d49125a665f3
Create Date: 2025-12-29 22:13:35.728982

"""

from alembic import op
from sqlalchemy import Column, DateTime

# revision identifiers, used by Alembic.
revision = "95651fc3abf7"
down_revision = "d49125a665f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the required train property columns."""
    op.add_column("devices", Column("last_seen", DateTime))
    op.execute("UPDATE devices SET last_seen = now()")


def downgrade() -> None:
    """Remove the new columns."""
    op.drop_column("trains", "last_seen")
