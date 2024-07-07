"""Background tasks."""

import logging
from asyncio import sleep

from httpx import AsyncClient

from mr_fat_controller.models import db_session

logger = logging.getLogger(__name__)


async def check_controllers() -> None:
    """Regular check that controllers are running."""
    try:
        async with AsyncClient(timeout=30) as client:  # noqa: F841
            while True:
                failed = False
                async for dbsession in db_session():  # noqa: B007
                    pass
                if failed:
                    await sleep(10)
                else:
                    await sleep(60)
    except Exception as e:
        logger.error(e)
