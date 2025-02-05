"""Link points to block detectors.

Revision ID: 0d8586eb471a
Revises: f11e0e87f8f6
Create Date: 2025-02-05 19:33:25.816321

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer

# revision identifiers, used by Alembic.
revision = "0d8586eb471a"
down_revision = "f11e0e87f8f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the necessary foreign keys to the points table."""
    op.add_column(
        "points", Column("through_block_detector_id", Integer, ForeignKey("block_detectors.id"), nullable=True)
    )
    op.add_column(
        "points", Column("diverge_block_detector_id", Integer, ForeignKey("block_detectors.id"), nullable=True)
    )
    op.add_column("points", Column("root_block_detector_id", Integer, ForeignKey("block_detectors.id"), nullable=True))


def downgrade() -> None:
    """Remove the foreign keys from the points table."""
    op.drop_column("points", "through_block_detector_id")
    op.drop_column("points", "diverge_block_detector_id")
    op.drop_column("points", "root_block_detector_id")
