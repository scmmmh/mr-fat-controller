"""Async WiThrottle client."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from mr_fat_controller.settings import settings
from mr_fat_controller.withrottle.util import split_str

logger = logging.getLogger(__name__)
power_initialised = False


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


async def process_power_status(line: str, writer: asyncio.StreamWriter, wt_to_mqtt: asyncio.Queue) -> None:
    """Process the data of a power status line."""
    global power_initialised  # noqa: PLW0603
    if line == "PPA0":
        await wt_to_mqtt.put({"type": "power", "state": "off"})
    elif line == "PPA1":
        await wt_to_mqtt.put({"type": "power", "state": "on"})
    elif line == "PPA2" and not power_initialised:
        writer.write(b"PPA0\n")
        await writer.drain()
        power_initialised = True


async def process_roster_list(line: str, writer: asyncio.StreamWriter, wt_to_mqtt: asyncio.Queue) -> None:
    """Process the roster list returned by the WiThrottle server."""
    line = line[2:]
    entries = split_str(line, "]\\[")
    for entry in entries[1:]:
        name, address, address_type = split_str(entry, "}|{")
        await wt_to_mqtt.put({"type": "train", "address": f"{address_type}{address}", "name": name})
        writer.write(f"MT+{address_type}{address}<;>{address_type}{address}\n".encode())
        await writer.drain()
        await asyncio.sleep(1)


async def process_train_added(line: str, wt_to_mqtt: asyncio.Queue) -> None:
    """Process confirmation that a train is added."""
    line = line[3:]
    address = line[: line.find("<;>")]
    await wt_to_mqtt.put({"type": "train", "address": address, "state": "on"})


async def process_train_functions(line: str, wt_to_mqtt: asyncio.Queue) -> None:
    """Process the list of train functions."""
    line = line[3:]
    address, data = split_str(line, "<;>")
    functions = {}
    for idx, label in enumerate(split_str(data, "]\\[")):
        if idx == 0:  # Ignore the first function
            continue
        elif label != "":  # Ignore any functions that don't have a label
            functions[str(idx - 1)] = {"name": label, "state": "off"}
    await wt_to_mqtt.put({"type": "train", "address": address, "functions": functions})


async def process_train_state(line: str, wt_to_mqtt: asyncio.Queue) -> None:
    """Process a single line of train state."""
    line = line[3:]
    address, data = split_str(line, "<;>")
    if data[0] == "F":
        if data[1] == "1":
            await wt_to_mqtt.put({"type": "train", "address": address, "functions": {data[2:]: {"state": "on"}}})
        else:
            await wt_to_mqtt.put({"type": "train", "address": address, "functions": {data[2:]: {"state": "off"}}})
    elif data[0] == "V":
        await wt_to_mqtt.put({"type": "train", "address": address, "speed": int(data[1:])})
    elif data[0] == "R":
        if data[1] == "0":
            await wt_to_mqtt.put({"type": "train", "address": address, "direction": "reverse"})
        else:
            await wt_to_mqtt.put({"type": "train", "address": address, "direction": "forward"})
    elif data[0] == "s":  # Ignore the speed step
        pass
    else:
        logger.debug(data)


async def withrottle_client(wt_to_mqtt: asyncio.Queue, mqtt_to_wt: asyncio.Queue):
    """Run the withrottle client."""
    global power_initialised  # noqa: PLW0603
    task_list = []
    try:
        while True:
            try:
                async with connect() as (reader, writer):
                    power_initialised = False
                    try:
                        logger.debug("WiThrottle client connected")

                        async def queue_listener() -> None:
                            while True:
                                msg = await mqtt_to_wt.get()
                                if msg["type"] == "power":
                                    if msg["state"] == "on":
                                        writer.write(b"PPA1\n")
                                    else:
                                        writer.write(b"PPA0\n")
                                    await writer.drain()
                                elif msg["type"] == "train":
                                    if "speed" in msg:
                                        writer.write(f"MTA{msg['address']}<;>V{msg['speed']}\n".encode())
                                        await wt_to_mqtt.put(
                                            {"type": "train", "address": msg["address"], "speed": msg["speed"]}
                                        )
                                    if "direction" in msg:
                                        if msg["direction"] == "forward":
                                            writer.write(f"MTA{msg['address']}<;>R1\n".encode())
                                            await wt_to_mqtt.put(
                                                {"type": "train", "address": msg["address"], "direction": "forward"}
                                            )
                                        else:
                                            writer.write(f"MTA{msg['address']}<;>R0\n".encode())
                                            await wt_to_mqtt.put(
                                                {"type": "train", "address": msg["address"], "direction": "forward"}
                                            )
                                    if "functions" in msg:
                                        for key, value in msg["functions"].items():
                                            if value == "on":
                                                writer.write(f"MTA{msg['address']}<;>f1{key}\n".encode())
                                            else:
                                                writer.write(f"MTA{msg['address']}<;>f0{key}\n".encode())
                                    await writer.drain()
                                else:
                                    logger.debug(msg)

                        task_list.append(asyncio.create_task(queue_listener()))

                        heartbeat_timeout = 10
                        while True:
                            task_list = [task for task in task_list if not task.done()]
                            try:
                                line = ""
                                async with asyncio.timeout(heartbeat_timeout):
                                    data = await reader.readline()
                                    if data == b"":
                                        raise ConnectionRefusedError()
                                    line = data.decode("utf-8").strip()
                                if line.startswith("MTA"):  # Multi Throttle action
                                    await process_train_state(line, wt_to_mqtt)
                                elif line.startswith("MTL"):  # Multi Throttle train functions
                                    await process_train_functions(line, wt_to_mqtt)
                                elif line.startswith("MT+"):  # Multi Throttle train added
                                    await process_train_added(line, wt_to_mqtt)
                                elif line.startswith("RL"):  # Roster list
                                    task_list.append(asyncio.create_task(process_roster_list(line, writer, wt_to_mqtt)))
                                elif line.startswith("PPA"):  # Power status
                                    await process_power_status(line, writer, wt_to_mqtt)
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
                        raise cre
                    except ConnectionResetError as cre:
                        raise cre
            except ConnectionRefusedError:
                logger.error("Lost connection to the WiThrottle server")
            except ConnectionResetError:
                logger.error("Lost connection to the WiThrottle server")
            for task in task_list:
                if not task.done():
                    task.cancel()
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        logger.debug("WiThrottle client shutting down")
        for task in task_list:
            if not task.done():
                task.cancel()
    except Exception as e:
        logger.error(e)
