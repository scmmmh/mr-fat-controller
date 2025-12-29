# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Server routes."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mr_fat_controller.api.block_detectors import router as block_detectors_router
from mr_fat_controller.api.devices import router as device_router
from mr_fat_controller.api.entities import router as entities_router
from mr_fat_controller.api.points import router as points_router
from mr_fat_controller.api.power_switches import router as power_switches_router
from mr_fat_controller.api.signal_automations import router as signal_automations_router
from mr_fat_controller.api.signals import router as signals_router
from mr_fat_controller.api.state import router as state_router
from mr_fat_controller.api.train_controllers import router as train_controllers_router
from mr_fat_controller.api.trains import router as trains_router
from mr_fat_controller.models import inject_db_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
router.include_router(block_detectors_router)
router.include_router(device_router)
router.include_router(entities_router)
router.include_router(power_switches_router)
router.include_router(points_router)
router.include_router(signal_automations_router)
router.include_router(signals_router)
router.include_router(state_router)
router.include_router(train_controllers_router)
router.include_router(trains_router)


class StatusModel(BaseModel):
    """Model for the status response."""

    ready: bool
    """Whether the server is ready."""


@router.get("/status", response_model=StatusModel)
async def status(dbsession: AsyncSession = Depends(inject_db_session)) -> dict:
    """Return the current server status."""
    try:
        await dbsession.execute(text("SELECT * FROM alembic_version"))
        return {"ready": True}
    except Exception as e:
        logger.error(e)
        return {"ready": False}
