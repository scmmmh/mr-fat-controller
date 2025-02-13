"""Create the trains table.

Revision ID: 8d72179919b8
Revises: 0d8586eb471a
Create Date: 2025-02-09 18:43:01.411186

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer, Unicode

# revision identifiers, used by Alembic.
revision = "8d72179919b8"
down_revision = "0d8586eb471a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the trains table."""
    op.create_table("trains", Column("id", Integer, primary_key=True), Column("name", Unicode(255)))
    op.create_table(
        "entity_trains",
        Column("entity_id", Integer, ForeignKey("entities.id"), primary_key=True, unique=True),
        Column("train_id", Integer, ForeignKey("trains.id"), primary_key=True),
    )


def downgrade() -> None:
    """Drop the trains table."""
    op.drop_table("entity_trains")
    op.drop_table("trains")
