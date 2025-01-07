"""API endpoints for block detectors."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select

from mr_fat_controller.models import BlockDetector, BlockDetectorModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/block-detectors")


class CreateBlockDetectorModel(BaseModel):
    """Model for validating a new BlockDetectors."""

    entity_id: int


@router.post("", response_model=BlockDetectorModel)
async def create_points(data: CreateBlockDetectorModel, dbsession=Depends(inject_db_session)) -> BlockDetector:
    """Create a new block detector."""
    block_detector = BlockDetector(
        entity_id=data.entity_id,
    )
    dbsession.add(block_detector)
    await dbsession.commit()
    await recalculate_state(dbsession)
    await full_state_refresh()
    return block_detector


@router.get("", response_model=list[BlockDetectorModel])
async def get_entities(dbsession=Depends(inject_db_session)) -> list[BlockDetector]:
    """Return all block detectors."""
    query = select(BlockDetector).order_by(BlockDetector.id)
    result = await dbsession.execute(query)
    return list(result.scalars())
