"""Create the train_controllers table.

Revision ID: d49125a665f3
Revises: 4b07c03857c6
Create Date: 2025-12-27 10:21:28.624761

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer, Unicode

# revision identifiers, used by Alembic.
revision = "d49125a665f3"
down_revision = "4b07c03857c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the train_controllers table."""
    op.create_table(
        "train_controllers",
        Column("id", Integer, primary_key=True),
        Column("train_id", Integer, ForeignKey("trains.id")),
        Column("name", Unicode(255)),
        Column("mode", Unicode(255)),
    )


def downgrade() -> None:
    """Drop the train_controllers table."""
    op.drop_table("train_controllers")
