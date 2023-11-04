# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The MR Fat Controller CLI application."""
import asyncio

from typer import Typer

from mr_fat_controller.cli import execute_setup

app = Typer()


@app.command()
def setup(*, drop_existing: bool = False, revert_last: bool = False) -> None:
    """Set up the database."""
    asyncio.run(execute_setup(drop_existing=drop_existing, revert_last=revert_last))


app()
