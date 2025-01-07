import asyncio
import json
import logging
import re
import signal
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from aiomqtt import Client

from mr_fat_controller.mqtt import mqtt_client
from mr_fat_controller.settings import settings


def split_str(text: str, sep: str) -> list[str]:
    parts = []
    while sep in text:
        parts.append(text[: text.find(sep)])
        text = text[text.find(sep) + len(sep) :]
    if text != "":
        parts.append(text)
    return parts


def slugify(text: str) -> str:
    text = re.sub(r"\s+", "-", text.lower())
    return text


WITHROTTLE_DEVICE = {
    "identifiers": [f"{slugify(settings.withrottle.name)}-withrottle-bridge"],
    "name": settings.withrottle.name,
}
logger = logging.getLogger(__name__)

power_state = "UNKNOWN"


@asynccontextmanager
async def withrottle_client() -> AsyncGenerator[tuple[asyncio.StreamReader, asyncio.StreamWriter], Any]:
    """Connect to the WiThrottle server and yield a reader/writer."""
    reader, writer = await asyncio.open_connection(settings.withrottle.host, settings.withrottle.port)
    writer.write(b"HUmrfatcontroller\nNMR Fat Controller\n")
    await writer.drain()
    yield reader, writer
    writer.write(b"Q")
    await writer.drain()


async def process_roster_list(line: str, client: Client) -> None:
    line = line[2:]
    entries = split_str(line, "]\\[")
    for entry in entries[1:]:
        name, address, address_type = split_str(entry, "}|{")
        await client.publish(
            f"mrfatcontroller/decoder/{slugify(settings.withrottle.name)}-{address_type}{address}-{slugify(name)}/config",
            json.dumps(
                {
                    "unique_id": f"{slugify(settings.withrottle.name)}-{address_type}{address}-{slugify(name)}",
                    "name": name,
                    "device_class": "decoder",
                    "state_topic": f"mrfatcontroller/decoder/{slugify(settings.withrottle.name)}-{address_type}{address}-{slugify(name)}/state",  # noqa: E501
                    "command_topic": f"mrfatcontroller/decoder/{slugify(settings.withrottle.name)}-{address_type}{address}-{slugify(name)}/set",  # noqa: E501
                    "device": WITHROTTLE_DEVICE,
                }
            ),
        )


async def process_power_status(line: str, client: Client) -> None:
    global power_state  # noqa: PLW0603
    if line == "PPA0":
        power_state = "OFF"
    elif line == "PPA1":
        power_state = "ON"
    elif line == "PPA2":
        power_state = "UNKNOWN"
    await client.publish(
        f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
        json.dumps({"state": power_state}),
    )


async def withrottle_heartbeat(timeout: int, writer: asyncio.StreamWriter) -> None:
    """Regularly send the heartbeat signal."""
    try:
        while True:
            await asyncio.sleep(timeout / 2)
            writer.write(b"*\n")
            await writer.drain()
    except Exception as e:
        logger.error(e)


async def withrottle_to_mqtt(wt_reader: asyncio.StreamReader, wt_writer: asyncio.StreamWriter, client: Client) -> None:
    try:
        heartbeat_task = None
        while True:
            line = (await wt_reader.readline()).decode("utf-8").strip()
            if line.startswith("RL"):  # Roster list
                await process_roster_list(line, client)
            elif line.startswith("PPA"):  # Power status
                await process_power_status(line, client)
            elif line.startswith("*"):  # Heartbeat timeout
                if heartbeat_task is not None and not heartbeat_task.done():
                    heartbeat_task.cancel()
                heartbeat_task = asyncio.create_task(withrottle_heartbeat(int(line[1:]), wt_writer))
            elif (
                line.startswith("VN")
                or line.startswith("HT")
                or line.startswith("Ht")
                or line.startswith("PFT")
                or line.startswith("PW")
            ):
                pass
            elif line:
                logger.debug(line)
    except asyncio.CancelledError:
        if heartbeat_task is not None and not heartbeat_task.done():
            heartbeat_task.cancel()


async def mqtt_to_withrottle(wt_writer: asyncio.StreamWriter, client: Client) -> None:
    try:
        await client.subscribe("mrfatcontroller/status")
        await client.subscribe(f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set")
        async for message in client.messages:
            if message.topic.value == "mrfatcontroller/status":
                if message.payload.decode("utf-8") == "online":
                    await client.publish(
                        f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",
                        json.dumps({"state": power_state}),
                    )
            elif (
                message.topic.value
                == f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set"
            ):
                data = json.loads(message.payload)
                if data["state"] == "ON":
                    wt_writer.write(b"PPA1\n")
                    await wt_writer.drain()
                elif data["state"] == "OFF":
                    wt_writer.write(b"PPA0\n")
                    await wt_writer.drain()
    except asyncio.CancelledError:
        pass


async def withrottle_mqtt_bridge():
    async with mqtt_client() as client:
        async with withrottle_client() as (wt_reader, wt_writer):
            await client.publish(
                f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/config",
                json.dumps(
                    {
                        "unique_id": f"{slugify(settings.withrottle.name)}-withrottle-power",
                        "name": f"{settings.withrottle.name} WiThrottle Power",
                        "device_class": "switch",
                        "state_topic": f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/state",  # noqa: E501
                        "command_topic": f"mrfatcontroller/switch/{slugify(settings.withrottle.name)}-withrottle-power/set",  # noqa: E501
                        "device": WITHROTTLE_DEVICE,
                    }
                ),
            )
            wt_mqtt = asyncio.create_task(withrottle_to_mqtt(wt_reader, wt_writer, client))
            mqtt_wt = asyncio.create_task(mqtt_to_withrottle(wt_writer, client))

            def sigint_handler() -> None:
                wt_mqtt.cancel()
                mqtt_wt.cancel()

            asyncio.get_running_loop().add_signal_handler(signal.SIGINT, sigint_handler)
            await wt_mqtt
            await mqtt_wt
