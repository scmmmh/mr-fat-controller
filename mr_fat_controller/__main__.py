# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The MR Fat Controller CLI application."""

import asyncio

from typer import Typer

from mr_fat_controller.cli import execute_setup
from mr_fat_controller.withrottle import withrottle_mqtt_bridge

app = Typer()


@app.command()
def setup(drop_existing: bool = False, revert_last: int = 0) -> None:  # noqa:FBT001, FBT002
    """Set up the database."""
    asyncio.run(execute_setup(drop_existing=drop_existing, revert_last=revert_last))


@app.command()
def withrottle_bridge() -> None:
    """Run the WiThrottle to MQTT Bridge."""
    asyncio.run(withrottle_mqtt_bridge())


app()
