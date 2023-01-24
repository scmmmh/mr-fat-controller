# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The MR Fat Controller CLI application."""
import typer

app = typer.Typer()


@app.command()
def setup() -> None:
    """Initialise or update the database and configuration."""
    pass


app()
