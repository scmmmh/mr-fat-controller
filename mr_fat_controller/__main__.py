# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The MR Fat Controller CLI application."""
import asyncio

from typer import Typer

from .cli import execute_setup


app = Typer()


@app.command()
def setup(drop_existing: bool = False) -> None:
    """Set up the database."""
    asyncio.run(execute_setup(drop_existing=drop_existing))


app()
