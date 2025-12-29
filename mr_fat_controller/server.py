# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The core MR Fat Controller server."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from httpx import AsyncClient

from mr_fat_controller import api, automation, mqtt
from mr_fat_controller.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:  # noqa: ARG001
    """Set up all lifespan activities."""
    mqtt_listener_task = asyncio.create_task(mqtt.mqtt_listener())
    await automation.setup_automations()
    yield
    mqtt_listener_task.cancel()


app = FastAPI(lifespan=lifespan)  # pyright: ignore[reportArgumentType]
app.include_router(api.router)

if settings.dev:

    @app.get("/app/{path:path}")
    async def ui_dev(path: str):
        """Proxy the development frontend server."""
        async with AsyncClient() as client:
            response = await client.get(f"http://localhost:5173/app/{path}")
            if response.status_code == 200:  # noqa:PLR2004
                return Response(content=response.content, media_type=response.headers["Content-Type"])
            else:
                raise HTTPException(response.status_code)

else:
    app.mount(
        "/app",
        StaticFiles(packages=[("mr_fat_controller", "frontend/dist")], html=True),  # pyright: ignore[reportCallIssue]
        name="app",
    )


@app.get("/", response_class=RedirectResponse)
def root() -> str:
    """Redirect to the frontend application."""
    return "/app"
