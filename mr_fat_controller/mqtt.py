"""MQTT functionality."""

import json
import logging
import ssl
from asyncio import sleep

from aiomqtt import Client
from pydantic import BaseModel, conlist
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import Device, Entity, Points, PointsModel, PowerSwitch, PowerSwitchModel, db_session
from mr_fat_controller.settings import settings
from mr_fat_controller.state import state_manager

logger = logging.getLogger(__name__)


def mqtt_client() -> Client:
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
    """Listener for the MQTT broker."""
    try:
        async with mqtt_client() as client:
            await client.subscribe("mrfatcontroller/+/+/config")
            await client.subscribe("mrfatcontroller/+/+/state")
            await client.publish("mrfatcontroller/status", "online")
            async for message in client.messages:
                try:
                    topic = tuple(message.topic.value.split("/"))
                    if topic[-1] == "config":
                        await register_new_entity(json.loads(message.payload))
                    elif topic[-1] == "state":
                        await state_manager.update_state(message.topic.value, json.loads(message.payload))
                except Exception as e:
                    logger.error(e)
        await sleep(5)
    except Exception as e:
        logger.error(e)


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
    device_class: str
    state_topic: str
    command_topic: str
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
                    attrs=data["device"],
                )
                dbsession.add(device)
            else:
                device.name = entity.device.name
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
                db_entity.name = entity.name
                db_entity.state_topic = entity.state_topic
                db_entity.command_topic = entity.command_topic
                db_entity.attrs = data
            await dbsession.commit()
            await recalculate_state(dbsession)
    except Exception as e:
        logger.error(e)


async def recalculate_state(dbsession: AsyncSession) -> None:
    query = select(Points).join(Points.entity).options(selectinload(Points.entity))
    result = await dbsession.execute(query)
    for points in result.scalars():
        await state_manager.add_state(
            points.entity.state_topic,
            {
                "type": "points",
                "model": PointsModel.model_validate(points).model_dump(),
                "state": "unknown",
            },
        )
    query = select(PowerSwitch).join(PowerSwitch.entity).options(selectinload(PowerSwitch.entity))
    result = await dbsession.execute(query)
    for points in result.scalars():
        await state_manager.add_state(
            points.entity.state_topic,
            {
                "type": "power_switch",
                "model": PowerSwitchModel.model_validate(points).model_dump(),
                "state": "unknown",
            },
        )
