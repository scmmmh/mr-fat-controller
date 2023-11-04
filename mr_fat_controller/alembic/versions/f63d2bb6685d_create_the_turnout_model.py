"""Create the turnout model.

Revision ID: f63d2bb6685d
Revises: f4ae106c7ce7
Create Date: 2023-11-04 15:05:03.223942

"""
from alembic import op
from sqlalchemy import Column, Unicode, ForeignKey
from sqlalchemy_json import NestedMutableJson

from mr_fat_controller.models.meta import metadata


# revision identifiers, used by Alembic.
revision = 'f63d2bb6685d'
down_revision = 'f4ae106c7ce7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the turnouts table."""
    op.create_table(
        "turnouts",
        metadata,
        Column("id", Unicode(64), primary_key=True),
        Column("controller_id", Unicode(64), ForeignKey("controllers.id")),
        Column("name", Unicode(255)),
        Column("state", Unicode(255)),
        Column("parameters", NestedMutableJson),
    )


def downgrade() -> None:
    """Drop the turnouts table."""
    op.drop_table("turnouts")
