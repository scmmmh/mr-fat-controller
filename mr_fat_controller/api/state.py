# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""State API."""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import Entity, Points, PowerSwitch, Train, db_session
from mr_fat_controller.mqtt import mqtt_client
from mr_fat_controller.state import state_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/state")


@router.websocket("")
async def state_socket(websocket: WebSocket) -> None:
    """Handle connections to the state Websocket."""
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
                if data["type"] == "set-points":
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
                elif data["type"] == "set-reverser":
                    async with db_session() as dbsession:
                        query = select(Entity).join(Entity.train).filter(Train.id == data["payload"]["id"])
                        entity = (await dbsession.execute(query)).scalar()
                        if entity is not None:
                            await client.publish(
                                entity.command_topic,  # type: ignore
                                json.dumps({"direction": data["payload"]["state"]}),
                            )
                elif data["type"] == "set-speed":
                    async with db_session() as dbsession:
                        query = select(Entity).join(Entity.train).filter(Train.id == data["payload"]["id"])
                        entity = (await dbsession.execute(query)).scalar()
                        if entity is not None:
                            await client.publish(
                                entity.command_topic,  # type: ignore
                                json.dumps({"speed": data["payload"]["state"]}),
                            )
                elif data["type"] == "toggle-decoder-function":
                    async with db_session() as dbsession:
                        query = select(Entity).join(Entity.train).filter(Train.id == data["payload"]["id"])
                        entity = (await dbsession.execute(query)).scalar()
                        if entity is not None:
                            functions = state_manager.state[entity.state_topic]["functions"]
                            if data["payload"]["state"] in functions:
                                if functions[data["payload"]["state"]]["state"] == "off":
                                    await client.publish(
                                        entity.command_topic,  # type: ignore
                                        json.dumps({"functions": {data["payload"]["state"]: "on"}}),
                                    )
                                else:
                                    await client.publish(
                                        entity.command_topic,  # type: ignore
                                        json.dumps({"functions": {data["payload"]["state"]: "off"}}),
                                    )
                else:
                    logger.debug(data)
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
