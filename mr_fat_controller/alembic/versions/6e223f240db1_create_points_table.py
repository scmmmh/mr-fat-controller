"""Create the points table.

Revision ID: 6e223f240db1
Revises: ca8797f8bc86
Create Date: 2024-07-10 21:56:19.147812

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer, Unicode

# revision identifiers, used by Alembic.
revision = "6e223f240db1"
down_revision = "ca8797f8bc86"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the points table."""
    op.create_table(
        "points",
        Column("id", Integer, primary_key=True),
        Column("entity_id", Integer, ForeignKey("entities.id")),
        Column("through_state", Unicode(255)),
        Column("diverge_state", Unicode(255)),
    )


def downgrade() -> None:
    """Drop the points table."""
    op.drop_table("points")
