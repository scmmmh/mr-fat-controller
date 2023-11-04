"""Background tasks."""
import logging

from asyncio import sleep
from httpx import AsyncClient, HTTPError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import db_session, Controller, Turnout

logger = logging.getLogger(__name__)


async def check_controllers() -> None:
    """Regular check that controllers are running."""
    try:
        async with AsyncClient() as client:
            while True:
                failed = False
                async for dbsession in db_session():
                    query = select(Controller).options(selectinload(Controller.turnouts))
                    for controller in (await dbsession.execute(query)).scalars():
                        try:
                            await client.get(f"{controller.baseurl}api")
                            controller.status = "ready"
                            await sync_turnouts(controller, dbsession, client)
                        except HTTPError:
                            controller.status = "disconnected"
                            failed = True
                    await dbsession.commit()
                if failed:
                    await sleep(10)
                else:
                    await sleep(60)
    except Exception as e:
        logger.error(e)


async def sync_turnouts(controller: Controller, dbsession: AsyncSession, client: AsyncClient) -> None:
    """Synchronise the configured turnouts to the controllers."""
    try:
        response = await client.get(f"{controller.baseurl}api/turnouts")
        remote_turnouts = response.json()
        for remote_turnout in remote_turnouts:
            found = False
            for turnout in controller.turnouts:
                if remote_turnout["id"] == turnout.id:
                    found = True
                    break
            if not found:
                await client.delete(f"{controller.baseurl}/api/turnouts/{remote_turnout['id']}")
        for turnout in controller.turnouts:
            found = False
            for remote_turnout in remote_turnouts:
                if remote_turnout["id"] == turnout.id:
                    found = True
                    turnout.state = remote_turnout["state"]
                    break
            if not found:
                response = await client.post(
                    f"{controller.baseurl}api/turnouts",
                    json={
                        "id": turnout.id,
                        "type": turnout.parameters["type"],
                        "params": dict([(k, v) for k, v in turnout.parameters.items() if k != "type"]),
                    },
                )
                if response.status_code == 200:
                    turnout.state = response.json()["state"]
    except Exception as e:
        logger.error(e)
