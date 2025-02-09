"""Async MQTT client for the WiThrottle bridge."""

import asyncio
import json
import logging

from mr_fat_controller.__about__ import __version__
from mr_fat_controller.mqtt import mqtt_client as mqtt_client_connection
from mr_fat_controller.settings import settings
from mr_fat_controller.state import state_manager
from mr_fat_controller.withrottle.util import slugify

logger = logging.getLogger(__name__)

WITHROTTLE_DEVICE = {
    "identifiers": [f"{slugify(settings.withrottle.name)}-withrottle-bridge"],
    "name": settings.withrottle.name,
    "manufacturer": "MR Fat Controller",
    "model": "WiThrottle Bridge",
    "sw_version": __version__,
}


async def publish_entities(client) -> None:
    """Publish all known entities for discovery."""
    await client.publish(
        f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/config",
        json.dumps(
            {
                "unique_id": f"{slugify(settings.withrottle.name)}-withrottle-power",
                "name": f"{settings.withrottle.name} WiThrottle Power",
                "device_class": "switch",
                "state_topic": f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                "command_topic": f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set",
                "device": WITHROTTLE_DEVICE,
            }
        ),
    )
    for state_topic, entity in state_manager.state.items():
        if entity["type"] == "decoder":
            await client.publish(
                f"{state_topic[:-6]}/config",
                json.dumps(
                    {
                        "unique_id": state_topic[:-6],
                        "name": entity["name"],
                        "device_class": "decoder",
                        "state_topic": state_topic,
                        "command_topic": f"{state_topic[:-6]}/set",
                        "device": WITHROTTLE_DEVICE,
                    }
                ),
            )
            entity["published"] = True


async def mqtt_client() -> None:
    """Run the mqtt client."""
    try:
        while True:
            async with mqtt_client_connection() as client:
                logger.debug("MQTT client connected")

                await publish_entities(client)

                async def state_listener(state: dict, topic: str | None) -> None:
                    """State listener for sending MQTT messages."""
                    for key, value in state.items():
                        if topic is None or key == topic:
                            if key == "power":
                                if "power" in state and value["state"] == "on":
                                    await client.publish(
                                        f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                                        json.dumps({"state": "ON"}),
                                    )
                                elif "power" in state and value["state"] == "off":
                                    await client.publish(
                                        f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                                        json.dumps({"state": "OFF"}),
                                    )
                            elif value["type"] == "decoder":
                                if "published" not in value:
                                    await publish_entities(client)
                                data = {
                                    "state": "OFF",
                                    "functions": value["functions"],
                                    "speed": value["speed"],
                                    "direction": value["direction"],
                                }
                                if value["state"] == "on":
                                    data["state"] = "ON"
                                await client.publish(key, json.dumps(data))

                await state_manager.add_listener(state_listener)

                await client.subscribe("mrfatcontroller/status")
                await client.subscribe(
                    f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set"
                )
                async for message in client.messages:
                    if message.topic.value == "mrfatcontroller/status":
                        if message.payload.decode("utf-8") == "online":  # type: ignore
                            await publish_entities(client)
                            await state_listener(state_manager.state, None)
                    elif (
                        message.topic.value
                        == f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set"
                    ):
                        data = json.loads(message.payload)  # type: ignore
                        if data["state"] == "ON":
                            await state_manager.update_state("power", {"state": "ON"})
                        else:
                            await state_manager.update_state("power", {"state": "OFF"})
                    else:
                        logger.debug(message.topic.value)
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        logger.debug("MQTT client shutting down")
