"""Create signal automations.

Revision ID: 78028e0d5172
Revises: 8d72179919b8
Create Date: 2025-02-22 20:22:32.307126
"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer, Unicode

# revision identifiers, used by Alembic.
revision = "78028e0d5172"
down_revision = "8d72179919b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the signal automations table and remove columns from signals."""
    op.create_table(
        "signal_automations",
        Column("id", Integer, primary_key=True),
        Column("signal_id", Integer, ForeignKey("signals.id")),
        Column("block_detector_id", Integer, ForeignKey("block_detectors.id")),
        Column("points_id", Integer, ForeignKey("points.id")),
        Column("points_state", Unicode(255)),
    )
    op.drop_column("points", "through_block_detector_id")
    op.drop_column("points", "diverge_block_detector_id")
    op.drop_column("points", "root_block_detector_id")
    op.drop_column("points", "through_signal_id")
    op.drop_column("points", "diverge_signal_id")
    op.drop_column("points", "root_signal_id")


def downgrade() -> None:
    """Drop the signal automations table and add the columns to signals."""
    op.drop_table("signal_automations")
    op.add_column(
        "points", Column("through_block_detector_id", Integer, ForeignKey("block_detectors.id"), nullable=True)
    )
    op.add_column(
        "points", Column("diverge_block_detector_id", Integer, ForeignKey("block_detectors.id"), nullable=True)
    )
    op.add_column("points", Column("root_block_detector_id", Integer, ForeignKey("block_detectors.id"), nullable=True))
    op.add_column("points", Column("through_signal_id", Integer, ForeignKey("signals.id"), nullable=True))
    op.add_column("points", Column("diverge_signal_id", Integer, ForeignKey("signals.id"), nullable=True))
    op.add_column("points", Column("root_signal_id", Integer, ForeignKey("signals.id"), nullable=True))
