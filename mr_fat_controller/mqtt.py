"""MQTT functionality."""

import json
import logging
import ssl
from asyncio import sleep
from threading import local  # pyright: ignore[reportAttributeAccessIssue]

from aiomqtt import Client
from pydantic import BaseModel, conlist
from sqlalchemy import select

from mr_fat_controller.models import Device, Entity, db_session
from mr_fat_controller.settings import settings

local_cache = local()
logger = logging.getLogger(__name__)

if settings.mqtt.tls:
    tls_context = ssl.create_default_context()
    if settings.mqtt.insecure_tls:
        tls_context.check_hostname = False
        tls_context.verify_mode = ssl.CERT_NONE
else:
    tls_context = None
local_cache.client = Client(
    settings.mqtt.host,
    port=settings.mqtt.port,
    tls_context=tls_context,
    username=settings.mqtt.username,
    password=settings.mqtt.password,
)


async def mqtt_listener() -> None:
    """Listener for the MQTT broker."""
    try:
        async with local_cache.client as client:
            await client.subscribe("mrfatcontroller/+/+/config")
            await client.subscribe("mrfatcontroller/+/+/state")
            await client.publish("mrfatcontroller/status", "online")
            async for message in client.messages:
                try:
                    topic = tuple(message.topic.value.split("/"))
                    if topic[-1] == "config":
                        await register_new_entity(json.loads(message.payload))
                    elif topic[-1] == "state":
                        await state_update(
                            message.topic.value, json.loads(message.payload)
                        )
                except Exception as e:
                    logger.error(e)
        await sleep(5)
    except Exception as e:
        logger.error(e)


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
            query = select(Device).filter(
                Device.external_id == entity.device.identifiers[0]
            )
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
                db_entity.state_topic = entity.state_topic
                db_entity.command_topic = entity.command_topic
                db_entity.attrs = data
            await dbsession.commit()
    except Exception as e:
        logger.error(e)


async def state_update(topic: str, data: dict) -> None:  # noqa: ARG001
    async with db_session() as dbsession:  # pyright: ignore[reportGeneralTypeIssues]
        query = select(Entity).filter(Entity.state_topic == topic)
        result = await dbsession.execute(query)
        entity = result.scalar()
        if entity is not None:
            print(entity)  # noqa: T201
