"""Server routes."""
from fastapi import APIRouter
from pydantic import BaseModel

from . import controllers


router = APIRouter(prefix='/api')
router.include_router(controllers.router)


class StatusModel(BaseModel):
    """Model for the status response."""

    ready: bool
    """Whether the server is ready."""


@router.get('/status', response_model=StatusModel)
def status() -> dict:
    """Return the current server status."""
    return {'ready': True}
