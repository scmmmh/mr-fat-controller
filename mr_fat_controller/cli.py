# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""CLI functions."""

import logging
from importlib import resources

from sqlalchemy.ext.asyncio import AsyncEngine

from mr_fat_controller.models import get_engine
from mr_fat_controller.settings import settings

logger = logging.getLogger(__name__)


async def execute_setup(*, drop_existing: bool = False, revert_last: int = 0) -> None:
    """Run the actual setup."""
    from alembic import command
    from alembic.config import Config

    alembic_base = resources.files("mr_fat_controller") / "alembic"
    with resources.as_file(alembic_base) as script_location:  # pyright: ignore[reportGeneralTypeIssues]
        alembic_config = Config()
        alembic_config.set_main_option("script_location", str(script_location))
        alembic_config.set_main_option("sqlalchemy.url", settings.dsn)

        def sync_db_ops(conn: AsyncEngine) -> None:
            """Run the commands synchronously."""
            try:
                alembic_config.attributes["connection"] = conn  # type: ignore
                if drop_existing:
                    logger.debug("Removing existing tables")
                    command.downgrade(alembic_config, "base")
                elif revert_last > 0:
                    logger.debug(f"Removing last {revert_last} migration(s)")
                    command.downgrade(alembic_config, f"-{revert_last}")
                logger.debug("Running upgrade")
                command.upgrade(alembic_config, "head")
            except Exception as e:
                logger.error(e)

        async with (
            get_engine().begin() as conn  # pyright: ignore[reportGeneralTypeIssues]
        ):
            await conn.run_sync(sync_db_ops)  # type: ignore
