"""Add train properties.

Revision ID: 4b07c03857c6
Revises: 78028e0d5172
Create Date: 2025-12-21 13:47:27.193240

"""

from alembic import op
from sqlalchemy import Column, Integer

# revision identifiers, used by Alembic.
revision = "4b07c03857c6"
down_revision = "78028e0d5172"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the required train property columns."""
    op.add_column("trains", Column("max_speed", Integer))
    op.execute("UPDATE trains SET max_speed = 0")


def downgrade() -> None:
    """Remove the new columns."""
    op.drop_column("trains", "max_speed")
