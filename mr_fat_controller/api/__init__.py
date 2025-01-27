"""Server routes."""

import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mr_fat_controller.api.block_detectors import router as block_detectors_router
from mr_fat_controller.api.devices import router as device_router
from mr_fat_controller.api.entities import router as entities_router
from mr_fat_controller.api.points import router as points_router
from mr_fat_controller.api.power_switches import router as power_switches_router
from mr_fat_controller.api.signals import router as signals_router
from mr_fat_controller.models import Entity, Points, PowerSwitch, db_session, inject_db_session
from mr_fat_controller.mqtt import mqtt_client
from mr_fat_controller.state import state_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
router.include_router(block_detectors_router)
router.include_router(device_router)
router.include_router(entities_router)
router.include_router(power_switches_router)
router.include_router(points_router)
router.include_router(signals_router)


class StatusModel(BaseModel):
    """Model for the status response."""

    ready: bool
    """Whether the server is ready."""


@router.get("/status", response_model=StatusModel)
async def status(dbsession: AsyncSession = Depends(inject_db_session)) -> dict:
    """Return the current server status."""
    try:
        await dbsession.execute(text("SELECT * FROM alembic_version"))
        return {"ready": True}
    except Exception as e:
        logger.error(e)
        return {"ready": False}


@router.websocket("/state")
async def state_socket(websocket: WebSocket) -> None:
    await websocket.accept()

    async def state_updates(state: dict, change_topic: str | None) -> None:
        if change_topic is not None and change_topic in state:
            await websocket.send_json({"type": "state", "payload": {change_topic: state[change_topic]}})
        else:
            await websocket.send_json({"type": "state", "payload": state})

    await state_manager.add_listener(state_updates)

    try:
        async with mqtt_client() as client:
            while True:
                data = await websocket.receive_json()
                if data["type"] == "refresh":
                    await client.publish("mrfatcontroller/status", "online")
                elif data["type"] == "set-points":
                    async with db_session() as dbsession:
                        query = (
                            select(Entity)
                            .join(Entity.points)
                            .filter(Points.id == data["payload"]["id"])
                            .options(selectinload(Entity.points))
                        )
                        result = await dbsession.execute(query)
                        entity = result.scalar()
                        if entity is not None:
                            if data["payload"]["state"] == "through":
                                await client.publish(
                                    entity.command_topic,  # type: ignore
                                    json.dumps({"state": entity.points.through_state}),
                                )
                            elif data["payload"]["state"] == "diverge":
                                await client.publish(
                                    entity.command_topic,  # type: ignore
                                    json.dumps({"state": entity.points.diverge_state}),
                                )
                elif data["type"] == "set-power_switch":
                    async with db_session() as dbsession:
                        query = select(Entity).join(Entity.power_switch).filter(PowerSwitch.id == data["payload"]["id"])
                        result = await dbsession.execute(query)
                        entity = result.scalar()
                        if entity is not None:
                            await client.publish(
                                entity.command_topic,  # type: ignore
                                json.dumps({"state": data["payload"]["state"].upper()}),
                            )
    except WebSocketDisconnect:
        logger.debug("Websocket disconnected")
    except Exception as e:
        logger.error(e)
        try:
            await websocket.close()
        except Exception as e2:
            logger.error(e2)
    finally:
        await state_manager.remove_listener(state_updates)
