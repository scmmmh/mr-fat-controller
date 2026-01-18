# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""MQTT functionality."""

import asyncio
import json
import logging
import ssl
from asyncio import sleep
from datetime import datetime, timezone
from typing import cast

from aiomqtt import Client
from pydantic import BaseModel, conlist
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from mr_fat_controller.models import (
    BlockDetector,
    BlockDetectorModel,
    Device,
    Entity,
    Points,
    PointsModel,
    PowerSwitch,
    PowerSwitchModel,
    Signal,
    SignalModel,
    Train,
    TrainModel,
    db_session,
)
from mr_fat_controller.settings import settings
from mr_fat_controller.state import state_manager

logger = logging.getLogger(__name__)


def mqtt_client() -> Client:
    """Return a correctly configured MQTT `Client`."""
    if settings.mqtt.tls:
        tls_context = ssl.create_default_context()
        if settings.mqtt.insecure_tls:
            tls_context.check_hostname = False
            tls_context.verify_mode = ssl.CERT_NONE
    else:
        tls_context = None
    return Client(
        settings.mqtt.host,
        port=settings.mqtt.port,
        tls_context=tls_context,
        username=settings.mqtt.username,
        password=settings.mqtt.password,
    )


async def mqtt_listener() -> None:
    """Run the MQTT broker listener."""
    running = True
    while running:
        try:
            await recalculate_state()
            async with mqtt_client() as client:
                await client.subscribe("mrfatcontroller/+/+/config")
                await client.subscribe("mrfatcontroller/+/+/state")
                await client.publish("mrfatcontroller/status", "online")
                async for message in client.messages:
                    try:
                        topic = tuple(message.topic.value.split("/"))
                        if topic[-1] == "config":
                            await register_new_entity(json.loads(cast(str, message.payload)))
                        elif topic[-1] == "state":
                            await state_manager.update_state(
                                message.topic.value, json.loads(cast(str, message.payload))
                            )
                            await update_device_active(message.topic.value)
                    except Exception as e:
                        logger.error(e)
        except asyncio.CancelledError:
            running = False
        except Exception as e:
            logger.error(e)
            await sleep(5)


async def full_state_refresh() -> None:
    """Request that all connected devices refresh their state."""
    async with mqtt_client() as client:
        await client.publish("mrfatcontroller/status", "online")


class NewDeviceModel(BaseModel):
    """Model for validating new devices."""

    identifiers: conlist(str, min_length=1)  # pyright: ignore[reportInvalidTypeForm]
    name: str


class NewEntityModel(BaseModel):
    """Model for validating new entities."""

    unique_id: str
    name: str
    device_class: str | None = None
    state_topic: str
    command_topic: str | None = None
    device: NewDeviceModel


async def register_new_entity(data: dict) -> None:
    """Register a new entity and device in the database."""
    try:
        entity = NewEntityModel(**data)
        async with (
            db_session() as dbsession  # pyright: ignore[reportGeneralTypeIssues]
        ):
            query = select(Device).filter(Device.external_id == entity.device.identifiers[0])
            result = await dbsession.execute(query)
            device = result.scalar()
            if device is None:
                device = Device(
                    external_id=entity.device.identifiers[0],
                    name=entity.device.name,
                    last_seen=datetime.now(tz=timezone.utc).replace(tzinfo=None),  # noqa: UP017
                    attrs=data["device"],
                )
                dbsession.add(device)
            else:
                device.name = entity.device.name  # type: ignore
                device.last_seen = datetime.now(tz=timezone.utc).replace(tzinfo=None)  # noqa: UP017
                device.attrs = data["device"]
            query = select(Entity).filter(Entity.external_id == entity.unique_id)
            result = await dbsession.execute(query)
            db_entity = result.scalar()
            del data["device"]
            if db_entity is None:
                db_entity = Entity(
                    name=entity.name,
                    external_id=entity.unique_id,
                    device=device,
                    device_class=entity.device_class,
                    state_topic=entity.state_topic,
                    command_topic=entity.command_topic,
                    attrs=data,
                )
                dbsession.add(db_entity)
            else:
                db_entity.device = device
                db_entity.name = entity.name  # type: ignore
                db_entity.state_topic = entity.state_topic  # type: ignore
                db_entity.command_topic = entity.command_topic  # type: ignore
                db_entity.attrs = data  # type: ignore
            await dbsession.commit()
            await recalculate_state()
    except Exception as e:
        logger.error(e)


async def recalculate_state() -> None:  # TODO: This needs a better name.
    """Recalculate the current state."""
    async with (
        db_session() as dbsession  # pyright: ignore[reportGeneralTypeIssues]
    ):
        query = select(BlockDetector).options(
            joinedload(BlockDetector.entity), selectinload(BlockDetector.signal_automations)
        )
        result = await dbsession.execute(query)
        for block_detector in result.scalars():
            await state_manager.add_state(
                block_detector.entity.state_topic,
                {
                    "type": "block_detector",
                    "model": BlockDetectorModel.model_validate(block_detector).model_dump(),
                    "state": "unknown",
                },
            )
        query = select(Points).options(joinedload(Points.entity), selectinload(Points.signal_automations))
        result = await dbsession.execute(query)
        for points in result.scalars():
            if points.entity.state_topic in state_manager:
                await state_manager.update_model(
                    points.entity.state_topic, PointsModel.model_validate(points).model_dump(), notify=False
                )
            else:
                await state_manager.add_state(
                    points.entity.state_topic,
                    {
                        "type": "points",
                        "model": PointsModel.model_validate(points).model_dump(),
                        "state": "unknown",
                    },
                    notify=False,
                )
        query = select(PowerSwitch).options(joinedload(PowerSwitch.entity))
        result = await dbsession.execute(query)
        for power_switch in result.scalars():
            if power_switch.entity.state_topic in state_manager:
                await state_manager.update_model(
                    power_switch.entity.state_topic,
                    PowerSwitchModel.model_validate(power_switch).model_dump(),
                    notify=False,
                )
            else:
                await state_manager.add_state(
                    power_switch.entity.state_topic,
                    {
                        "type": "power_switch",
                        "model": PowerSwitchModel.model_validate(power_switch).model_dump(),
                        "state": "unknown",
                    },
                    notify=False,
                )
        query = select(Signal).options(joinedload(Signal.entity), selectinload(Signal.signal_automations))
        result = await dbsession.execute(query)
        for signal in result.scalars():
            if signal.entity.state_topic in state_manager:
                await state_manager.update_model(
                    signal.entity.state_topic, SignalModel.model_validate(signal).model_dump(), notify=False
                )
            else:
                await state_manager.add_state(
                    signal.entity.state_topic,
                    {
                        "type": "signal",
                        "model": SignalModel.model_validate(signal).model_dump(),
                        "state": "unknown",
                    },
                    notify=False,
                )
        query = select(Train).options(selectinload(Train.entity)).options(selectinload(Train.controllers))
        result = await dbsession.execute(query)
        for train in result.scalars():
            if train.entity.state_topic in state_manager:
                await state_manager.update_model(
                    train.entity.state_topic, TrainModel.model_validate(train).model_dump(), notify=False
                )
            else:
                await state_manager.add_state(
                    train.entity.state_topic,
                    {
                        "type": "train",
                        "model": TrainModel.model_validate(train).model_dump(),
                        "state": "on",
                        "speed": 0,
                        "direction": "forward",
                        "functions": {},
                    },
                    notify=False,
                )
    await state_manager._notify(None)


async def update_device_active(entity_topic) -> None:
    """Update the database to note that a device was active."""
    async with (
        db_session() as dbsession  # pyright: ignore[reportGeneralTypeIssues]
    ):
        query = (
            select(Entity).filter(Entity.external_id == entity_topic.split("/")[2]).options(joinedload(Entity.device))
        )
        result = await dbsession.execute(query)
        entity = result.scalar()
        if entity is not None:
            entity.device.last_seen = datetime.now(tz=timezone.utc).replace(tzinfo=None)  # noqa: UP017
            await dbsession.commit()
