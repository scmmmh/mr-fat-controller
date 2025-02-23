# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for block detectors."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from mr_fat_controller.models import BlockDetector, BlockDetectorModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/block-detectors")


class CreateBlockDetectorModel(BaseModel):
    """Model for validating a new BlockDetectors."""

    entity_id: int


@router.post("", response_model=BlockDetectorModel)
async def create_block_detector(data: CreateBlockDetectorModel, dbsession=Depends(inject_db_session)) -> BlockDetector:
    """Create a new block detector."""
    block_detector = BlockDetector(
        entity_id=data.entity_id,
    )
    dbsession.add(block_detector)
    await dbsession.commit()
    await recalculate_state()
    await full_state_refresh()
    return block_detector


@router.get("", response_model=list[BlockDetectorModel])
async def get_block_detectors(dbsession=Depends(inject_db_session)) -> list[BlockDetector]:
    """Return all block detectors."""
    query = (
        select(BlockDetector)
        .order_by(BlockDetector.id)
        .options(joinedload(BlockDetector.entity), selectinload(BlockDetector.signal_automations))
    )
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{bid}", response_model=BlockDetectorModel)
async def get_block_detector(bid: int, dbsession=Depends(inject_db_session)) -> BlockDetector:
    """Return one block detectors."""
    query = (
        select(BlockDetector)
        .filter(BlockDetector.id == bid)
        .options(joinedload(BlockDetector.entity), selectinload(BlockDetector.signal_automations))
    )
    block_detector = (await dbsession.execute(query)).scalar()
    if block_detector is not None:
        return block_detector
    else:
        raise HTTPException(404, "No such block detector found")


@router.delete("/{bid}", status_code=204)
async def delete_block_detector(bid: int, dbsession=Depends(inject_db_session)) -> None:
    """Delete a block detectors."""
    query = (
        select(BlockDetector)
        .filter(BlockDetector.id == bid)
        .options(joinedload(BlockDetector.entity), selectinload(BlockDetector.signal_automations))
    )
    block_detector = (await dbsession.execute(query)).scalar()
    if block_detector is not None:
        await dbsession.delete(block_detector)
        await dbsession.commit()
        await recalculate_state()
        await full_state_refresh()
    else:
        raise HTTPException(404, "No such block detector found")
