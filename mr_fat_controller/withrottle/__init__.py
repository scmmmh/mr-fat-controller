# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""WiThrottle to MQTT bridge."""

import asyncio
import logging
import signal

from mr_fat_controller.withrottle.client import withrottle_client
from mr_fat_controller.withrottle.mqtt import mqtt_client

logger = logging.getLogger(__name__)


async def withrottle_mqtt_bridge():
    """Run the WiThrottle to MQTT bridge."""
    wt_client_task = None
    mqtt_client_task = None

    def sigint_handler() -> None:
        if wt_client_task is not None and not wt_client_task.done():
            wt_client_task.cancel()
        if mqtt_client_task is not None and not mqtt_client_task.done():
            mqtt_client_task.cancel()

    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, sigint_handler)

    wt_client_task = asyncio.create_task(withrottle_client())
    mqtt_client_task = asyncio.create_task(mqtt_client())

    await asyncio.gather(wt_client_task, mqtt_client_task)

    if wt_client_task is not None and not wt_client_task.done():
        wt_client_task.cancel()
    if mqtt_client_task is not None and not mqtt_client_task.done():
        mqtt_client_task.cancel()
