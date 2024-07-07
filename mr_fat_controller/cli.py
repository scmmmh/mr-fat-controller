"""CLI functions."""

import logging
from importlib import resources

from sqlalchemy.ext.asyncio import AsyncEngine

from mr_fat_controller.models import get_engine
from mr_fat_controller.settings import settings

logger = logging.getLogger(__name__)


async def execute_setup(*, drop_existing: bool = False, revert_last: bool = False) -> None:
    """Run the actual setup."""
    from alembic import command
    from alembic.config import Config

    alembic_base = resources.files("mr_fat_controller") / "alembic"
    with resources.as_file(alembic_base) as script_location:
        alembic_config = Config()
        alembic_config.set_main_option("script_location", str(script_location))
        alembic_config.set_main_option("sqlalchemy.url", settings.dsn)

        def sync_db_ops(conn: AsyncEngine) -> None:
            """Run the commands synchronously."""
            try:
                alembic_config.attributes["connection"] = conn
                if drop_existing:
                    logger.debug("Removing existing tables")
                    command.downgrade(alembic_config, "base")
                elif revert_last:
                    logger.debug("Removing last migration")
                    command.downgrade(alembic_config, "-1")
                logger.debug("Running upgrade")
                command.upgrade(alembic_config, "head")
            except Exception as e:
                logger.error(e)

        async with get_engine().begin() as conn:
            await conn.run_sync(sync_db_ops)
