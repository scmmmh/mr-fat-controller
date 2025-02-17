"""Async MQTT client for the WiThrottle bridge."""

import asyncio
import json
import logging

from mr_fat_controller.__about__ import __version__
from mr_fat_controller.mqtt import mqtt_client as mqtt_client_connection
from mr_fat_controller.settings import settings
from mr_fat_controller.withrottle.util import slugify

logger = logging.getLogger(__name__)
state = {}

WITHROTTLE_DEVICE = {
    "identifiers": [f"{slugify(settings.withrottle.name)}-withrottle-bridge"],
    "name": settings.withrottle.name,
    "manufacturer": "MR Fat Controller",
    "model": "WiThrottle Bridge",
    "sw_version": __version__,
}


async def publish_full_state(client, only_publish: str | None = None) -> None:
    """Publish the full current state."""
    for key, value in state.items():
        if only_publish is not None and only_publish != key:
            continue
        if key == "power":
            if state["power"]["state"] == "on":
                await client.publish(
                    f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                    json.dumps({"state": "ON"}),
                )
            else:
                await client.publish(
                    f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                    json.dumps({"state": "OFF"}),
                )
        elif value["type"] == "train":
            msg = {"state": value["state"].upper()}
            if "speed" in value:
                msg["speed"] = value["speed"]
            if "direction" in value:
                msg["direction"] = value["direction"]
            if "functions" in value:
                msg["functions"] = value["functions"]
            await client.publish(f"mrfatcontroller/train/{key}/state", json.dumps(msg))


async def publish_entities(client) -> None:
    """Publish all known entities for discovery."""
    for key, value in state.items():
        if key == "power":
            await client.publish(
                f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/config",
                json.dumps(
                    {
                        "unique_id": f"{slugify(settings.withrottle.name)}-withrottle-power",
                        "name": f"{settings.withrottle.name} WiThrottle Power",
                        "device_class": "switch",
                        "state_topic": f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",  # noqa:E501
                        "command_topic": f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set",  # noqa:E501
                        "device": WITHROTTLE_DEVICE,
                    }
                ),
            )
        elif value["type"] == "train":
            await client.publish(
                f"mrfatcontroller/train/{key}/config",
                json.dumps(
                    {
                        "unique_id": f"mrfatcontroller/train/{key}",
                        "name": value["name"],
                        "device_class": "train",
                        "state_topic": f"mrfatcontroller/train/{key}/state",
                        "command_topic": f"mrfatcontroller/train/{key}/set",
                        "device": WITHROTTLE_DEVICE,
                    }
                ),
            )
    await asyncio.sleep(1)
    await publish_full_state(client)


async def mqtt_client(wt_to_mqtt: asyncio.Queue, mqtt_to_wt: asyncio.Queue) -> None:
    """Run the mqtt client."""
    queue_listener_task = None
    try:
        while True:
            async with mqtt_client_connection() as client:
                logger.debug("MQTT client connected")

                await publish_entities(client)

                async def queue_listener() -> None:
                    while True:
                        msg = await wt_to_mqtt.get()
                        if msg["type"] == "power":
                            state["power"] = {"type": "power", "state": msg["state"]}
                            if state["power"] == "on":
                                await client.publish(
                                    f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                                    json.dumps({"state": "ON"}),
                                )
                            else:
                                await client.publish(
                                    f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                                    json.dumps({"state": "OFF"}),
                                )
                        elif msg["type"] == "train":
                            if msg["address"] not in state:
                                state[msg["address"]] = {"type": "train", "name": msg["name"], "state": "OFF"}
                                await publish_entities(client)
                            if "state" in msg:
                                state[msg["address"]]["state"] = msg["state"]
                            if "speed" in msg:
                                state[msg["address"]]["speed"] = msg["speed"]
                            if "direction" in msg:
                                state[msg["address"]]["direction"] = msg["direction"]
                            if "functions" in msg:
                                if "functions" not in state[msg["address"]]:
                                    state[msg["address"]]["functions"] = msg["functions"]
                                else:
                                    for fn_key, fn_value in msg["functions"].items():
                                        if fn_key in state[msg["address"]]["functions"]:
                                            state[msg["address"]]["functions"][fn_key]["state"] = fn_value["state"]
                            await publish_full_state(client, msg["address"])
                        else:
                            logger.debug(msg)

                queue_listener_task = asyncio.create_task(queue_listener())

                await client.subscribe("mrfatcontroller/status")
                await client.subscribe(
                    f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set"
                )
                await client.subscribe("mrfatcontroller/train/+/set")
                async for message in client.messages:
                    if message.topic.value == "mrfatcontroller/status":
                        if message.payload.decode("utf-8") == "online":  # type: ignore
                            await publish_entities(client)
                    elif (
                        message.topic.value
                        == f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set"
                    ):
                        data = json.loads(message.payload)  # type: ignore
                        if data["state"] == "ON":
                            await mqtt_to_wt.put({"type": "power", "state": "on"})
                        else:
                            await mqtt_to_wt.put({"type": "power", "state": "off"})
                    elif message.topic.value.startswith("mrfatcontroller/train/"):
                        _, _, address, _ = message.topic.value.split("/")
                        if address in state:
                            data = json.loads(message.payload)  # type:ignore
                            if "speed" in data:
                                await mqtt_to_wt.put({"type": "train", "address": address, "speed": data["speed"]})
                            if "direction" in data:
                                await mqtt_to_wt.put(
                                    {"type": "train", "address": address, "direction": data["direction"]}
                                )
                            if "functions" in data:
                                await mqtt_to_wt.put(
                                    {"type": "train", "address": address, "functions": data["functions"]}
                                )
                        else:
                            logger.debug(f"Address {address} not found in state")
                    else:
                        logger.debug(f"Unknown topic {message.topic.value}")
            if queue_listener_task is not None and not queue_listener_task.done():
                queue_listener_task.cancel()
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        logger.debug("MQTT client shutting down")
        if queue_listener_task is not None and not queue_listener_task.done():
            queue_listener_task.cancel()
