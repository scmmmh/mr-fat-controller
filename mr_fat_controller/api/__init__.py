"""Server routes."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mr_fat_controller.api.entities import router as entity_router
from mr_fat_controller.api.points import router as points_router
from mr_fat_controller.models import inject_db_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
router.include_router(entity_router)
router.include_router(points_router)


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
