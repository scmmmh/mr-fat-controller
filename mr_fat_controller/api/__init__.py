"""Server routes."""
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from . import controllers
from ..models import db_session


logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api')
router.include_router(controllers.router)


class StatusModel(BaseModel):
    """Model for the status response."""

    ready: bool
    """Whether the server is ready."""


@router.get('/status', response_model=StatusModel)
async def status(dbsession: AsyncSession = Depends(db_session)) -> dict:
    """Return the current server status."""
    try:
        await dbsession.execute(text('SELECT * FROM alembic_version'))
        return {'ready': True}
    except Exception as e:       # noqa: cov
        logger.error(e)          # noqa: cov
        return {'ready': False}  # noqa: cov
