"""Create the power switches table.

Revision ID: 2b85d6115293
Revises: 6e223f240db1
Create Date: 2024-12-27 15:55:46.519722

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer

# revision identifiers, used by Alembic.
revision = "2b85d6115293"
down_revision = "6e223f240db1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the power switches table."""
    op.create_table(
        "power_switches",
        Column("id", Integer, primary_key=True),
        Column("entity_id", Integer, ForeignKey("entities.id")),
    )


def downgrade() -> None:
    """Drop the power switches table."""
    op.drop_table("power_switches")
