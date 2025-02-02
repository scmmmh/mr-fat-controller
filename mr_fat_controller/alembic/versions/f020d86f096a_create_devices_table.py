# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Create devices table.

Revision ID: f020d86f096a
Revises:
Create Date: 2024-07-07 22:02:18.792802

"""

from alembic import op
from sqlalchemy import Column, Integer, Unicode
from sqlalchemy_json import NestedMutableJson

# revision identifiers, used by Alembic.
revision = "f020d86f096a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the devices table."""
    op.create_table(
        "devices",
        Column("id", Integer, primary_key=True),
        Column("external_id", Unicode(255), unique=True),
        Column("name", Unicode(255)),
        Column("attrs", NestedMutableJson),
    )


def downgrade() -> None:
    """Drop the devices table."""
    op.drop_table("devices")
