"""Async WiThrottle client."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from mr_fat_controller.settings import settings
from mr_fat_controller.state import state_manager
from mr_fat_controller.withrottle.util import slugify, split_str

logger = logging.getLogger(__name__)


@asynccontextmanager
async def connect() -> AsyncGenerator[tuple[asyncio.StreamReader, asyncio.StreamWriter], Any]:
    """Connect to the WiThrottle server and yield a reader/writer."""
    reader, writer = await asyncio.open_connection(host=settings.withrottle.host, port=settings.withrottle.port)
    writer.write(b"HUmrfatcontroller\nNMR Fat Controller\n")
    await writer.drain()
    try:
        yield reader, writer
    finally:
        try:
            writer.close()
        except Exception as closing_exception:
            raise closing_exception


async def process_power_status(line: str, writer: asyncio.StreamWriter) -> None:
    """Process the data of a power status line."""
    if line == "PPA0":
        power_state = "OFF"
    elif line == "PPA1":
        power_state = "ON"
    elif line == "PPA2":
        power_state = "UNKNOWN"
    if state_manager.state["power"]["state"] == "unknown" and power_state == "UNKNOWN":
        writer.write(b"PPA0\n")
        await writer.drain()
    elif state_manager.state["power"]["state"] != power_state.lower() and power_state != "UNKNOWN":
        await state_manager.update_state("power", {"state": power_state})


async def process_roster_list(line: str, writer: asyncio.StreamWriter) -> None:
    """Process the roster list returned by the WiThrottle server."""
    line = line[2:]
    entries = split_str(line, "]\\[")
    for entry in entries[1:]:
        name, address, address_type = split_str(entry, "}|{")
        topic = f"mrfatcontroller/decoder/{slugify(settings.withrottle.name)}-{address_type}{address}/state"
        if topic in state_manager:
            del state_manager.state[topic]
        await state_manager.add_state(
            topic,
            {
                "type": "decoder",
                "state": "off",
                "functions": {},
                "speed": 0,
                "direction": "forward",
                "name": name,
            },
        )
        writer.write(f"MT+{address_type}{address}<;>{address_type}{address}\n".encode())
        await writer.drain()
        await asyncio.sleep(1)


async def process_decoder_added(line: str) -> None:
    """Process confirmation that a decoder is added."""
    line = line[3:]
    address = line[: line.find("<;>")]
    topic = f"mrfatcontroller/decoder/{slugify(settings.withrottle.name)}-{address}/state"
    await state_manager.update_state(topic, {"type": "decoder", "state": "ON"})


async def process_decoder_functions(line: str) -> None:
    """Process the list of decoder functions."""
    line = line[3:]
    address, data = split_str(line, "<;>")
    topic = f"mrfatcontroller/decoder/{slugify(settings.withrottle.name)}-{address}/state"
    functions = {}
    for idx, label in enumerate(split_str(data, "]\\[")):
        if idx == 0:  # Ignore the first function
            continue
        elif label != "":  # Ignore any functions that don't have a label
            functions[idx] = {"label": label, "state": "off"}
    await state_manager.update_state(topic, {"type": "decoder", "functions": functions})


async def process_decoder_state(line: str) -> None:
    """Process a single line of decoder state."""
    line = line[3:]
    address, data = split_str(line, "<;>")
    topic = f"mrfatcontroller/decoder/{slugify(settings.withrottle.name)}-{address}/state"
    if data[0] == "F":
        if topic in state_manager:
            functions = state_manager.state[topic]["functions"]
            fid = int(data[2:])
            if fid in functions:
                if data[1] == "1":
                    functions[fid]["state"] = "on"
                else:
                    functions[fid]["state"] = "off"
            await state_manager.update_state(topic, {"type": "decoder", "functions": functions})
    elif data[0] == "V":
        await state_manager.update_state(topic, {"type": "decoder", "speed": int(data[1:])})
    elif data[0] == "R":
        if data[1] == "0":
            await state_manager.update_state(topic, {"type": "decoder", "direction": "reverse"})
        else:
            await state_manager.update_state(topic, {"type": "decoder", "direction": "forward"})
    elif data[0] == "s":  # Ignore the speed step
        pass
    else:
        logger.debug(data)


async def withrottle_client():
    """Run the withrottle client."""
    try:
        while True:
            await state_manager.clear_state()
            await state_manager.add_state("power", {"type": "power_switch", "state": "unknown"})
            try:
                async with connect() as (reader, writer):
                    try:
                        logger.debug("WiThrottle client connected")

                        async def state_listener(state: dict, topic: str | None) -> None:
                            """Send data on state changes."""
                            if topic == "power":
                                if state["power"]["state"] == "on":
                                    writer.write(b"PPA1\n")
                                else:
                                    writer.write(b"PPA0\n")
                                await writer.drain()

                        await state_manager.add_listener(state_listener)

                        heartbeat_timeout = 10
                        task_list = []
                        while True:
                            task_list = [task for task in task_list if not task.done()]
                            try:
                                async with asyncio.timeout(heartbeat_timeout):
                                    data = await reader.readline()
                                    if data == b"":
                                        raise ConnectionRefusedError()
                                    line = data.decode("utf-8").strip()
                                if line.startswith("MTA"):  # Multi Throttle action
                                    await process_decoder_state(line)
                                elif line.startswith("MTL"):  # Multi Throttle decoder functions
                                    await process_decoder_functions(line)
                                elif line.startswith("MT+"):  # Multi Throttle decoder added
                                    await process_decoder_added(line)
                                elif line.startswith("RL"):  # Roster list
                                    task_list.append(asyncio.create_task(process_roster_list(line, writer)))
                                elif line.startswith("PPA"):  # Power status
                                    await process_power_status(line, writer)
                                elif line.startswith("*"):  # Heartbeat timeout
                                    heartbeat_timeout = int(line[1:]) * 0.75
                                elif (
                                    line.startswith("VN")
                                    or line.startswith("HT")
                                    or line.startswith("Ht")
                                    or line.startswith("PFT")
                                    or line.startswith("PW")
                                    or line.startswith("PTT")
                                    or line.startswith("PRT")
                                    or line.startswith("RCC")
                                ):
                                    pass  # Ignore stuff that is not supported
                                elif line:
                                    logger.debug(line)
                            except TimeoutError:
                                writer.write(b"*\n")
                                await writer.drain()
                    except asyncio.CancelledError as ce:
                        writer.write(b"Q\n")
                        await writer.drain()
                        raise ce
                    except ConnectionRefusedError as cre:
                        await state_manager.remove_listener(state_listener)
                        raise cre
            except ConnectionRefusedError:
                logger.error("Lost connection to the WiThrottle server")
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        logger.debug("WiThrottle client shutting down")
    except Exception as e:
        logger.error(e)
