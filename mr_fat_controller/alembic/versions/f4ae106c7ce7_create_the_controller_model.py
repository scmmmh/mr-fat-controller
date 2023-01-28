"""Create the controller model.

Revision ID: f4ae106c7ce7
Revises:
Create Date: 2023-01-28 17:10:16.922546

"""
from alembic import op
from sqlalchemy import Column, Unicode

from mr_fat_controller.models.meta import metadata


# revision identifiers, used by Alembic.
revision = 'f4ae106c7ce7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the controllers table."""
    op.create_table('controllers',
                    metadata,
                    Column('id', Unicode(255), primary_key=True),
                    Column('baseurl', Unicode(255)),
                    Column('name', Unicode(255)),
                    Column('status', Unicode(255)))


def downgrade() -> None:
    """Drop the controllers table."""
    op.drop_table('controllers')
