"""Background tasks."""
import logging

from asyncio import sleep
from httpx import AsyncClient, HTTPError
from sqlalchemy import select

from mr_fat_controller.models import db_session, Controller

logger = logging.getLogger(__name__)


async def check_controllers() -> None:
    """Regular check that controllers are running."""
    try:
        async with AsyncClient() as client:
            while True:
                async for dbsession in db_session():
                    query = select(Controller)
                    for controller in (await dbsession.execute(query)).scalars():
                        try:
                            await client.get(f"{controller.baseurl}api")
                            controller.status = "ready"
                        except HTTPError:
                            controller.status = "disconnected"
                    await dbsession.commit()
                await sleep(60)
    except Exception as e:
        logger.error(e)
