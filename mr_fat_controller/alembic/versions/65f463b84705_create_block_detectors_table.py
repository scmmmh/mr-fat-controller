"""Create Block Detectors table.

Revision ID: 65f463b84705
Revises: 2b85d6115293
Create Date: 2025-01-07 21:48:06.024419

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer

# revision identifiers, used by Alembic.
revision = "65f463b84705"
down_revision = "2b85d6115293"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the block detectors table."""
    op.create_table(
        "block_detectors",
        Column("id", Integer, primary_key=True),
        Column("entity_id", Integer, ForeignKey("entities.id")),
    )


def downgrade() -> None:
    """Drop the block detectors table."""
    op.drop_table("block_detectors")
