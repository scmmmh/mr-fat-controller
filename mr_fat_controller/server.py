# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The core MR Fat Controller server."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from mr_fat_controller import api, automation, mqtt


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:  # noqa: ARG001
    """Set up all lifespan activities."""
    mqtt_listener_task = asyncio.create_task(mqtt.mqtt_listener())
    await automation.setup_automations()
    yield
    mqtt_listener_task.cancel()


app = FastAPI(lifespan=lifespan)  # pyright: ignore[reportArgumentType]
app.include_router(api.router)
app.mount(
    "/app",
    StaticFiles(packages=[("mr_fat_controller", "frontend/dist")], html=True),  # pyright: ignore[reportCallIssue]
    name="app",
)


@app.get("/", response_class=RedirectResponse)
def root() -> str:
    """Redirect to the frontend application."""
    return "/app"
