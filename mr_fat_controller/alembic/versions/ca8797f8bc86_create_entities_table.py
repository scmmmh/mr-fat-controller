# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Create entities table.

Revision ID: ca8797f8bc86
Revises: f020d86f096a
Create Date: 2024-07-07 22:16:21.200320

"""

from alembic import op
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy_json import NestedMutableJson

# revision identifiers, used by Alembic.
revision = "ca8797f8bc86"
down_revision = "f020d86f096a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the entities table."""
    op.create_table(
        "entities",
        Column("id", Integer, primary_key=True),
        Column("external_id", Unicode(255), unique=True),
        Column("device_id", Integer, ForeignKey("devices.id")),
        Column("name", Unicode(255)),
        Column("device_class", Unicode(255)),
        Column("state_topic", Unicode(255), unique=True),
        Column("command_topic", Unicode(255), nullable=True),
        Column("attrs", NestedMutableJson),
    )


def downgrade() -> None:
    """Drop the entities table."""
    op.drop_table("entities")
