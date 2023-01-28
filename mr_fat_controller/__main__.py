# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The MR Fat Controller CLI application."""
import asyncio
import logging

from importlib import resources
from sqlalchemy.ext.asyncio import AsyncEngine
from typer import Typer

from .models import engine
from .settings import settings


logger = logging.getLogger(__name__)
app = Typer()


@app.command()
def setup(drop_existing: bool = False) -> None:
    """Set up the database."""
    async def run_async() -> None:
        """Run as an async command."""
        from alembic.config import Config
        from alembic import command

        alembic_config = Config()
        alembic_config.set_main_option('script_location', str(resources.path('mr_fat_controller', 'alembic')))
        alembic_config.set_main_option('sqlalchemy.url', settings['dsn'])

        def sync_db_ops(conn: AsyncEngine) -> None:
            """Run the commands synchronously."""
            try:
                alembic_config.attributes['connection'] = conn
                if drop_existing:
                    logger.debug('Removing existing tables')
                    command.downgrade(alembic_config, 'base')
                logger.debug('Running upgrade')
                command.upgrade(alembic_config, 'head')
            except Exception as e:
                logger.error(e)

        async with engine.begin() as conn:
            await conn.run_sync(sync_db_ops)

    asyncio.run(run_async())


app()
