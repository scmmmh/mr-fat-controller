# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for handling points."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from mr_fat_controller.models import Points, PointsModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/points")


class CreatePointsModel(BaseModel):
    """Model for validating a new Points."""

    entity_id: int
    through_state: str
    diverge_state: str


@router.post("", response_model=PointsModel)
async def create_points(data: CreatePointsModel, dbsession=Depends(inject_db_session)) -> Points:
    """Create new points."""
    points = Points(
        entity_id=data.entity_id,
        through_state=data.through_state,
        diverge_state=data.diverge_state,
    )
    dbsession.add(points)
    await dbsession.commit()
    await recalculate_state()
    await full_state_refresh()
    return await get_points(points.id, dbsession=dbsession)  # pyright: ignore [reportArgumentType]


@router.get("", response_model=list[PointsModel])
async def get_all_points(dbsession=Depends(inject_db_session)) -> list[Points]:
    """Return all points."""
    query = (
        select(Points).order_by(Points.id).options(joinedload(Points.entity), selectinload(Points.signal_automations))
    )
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{pid}", response_model=PointsModel)
async def get_points(pid: int, dbsession=Depends(inject_db_session)) -> Points:
    """Return a single set of points."""
    query = (
        select(Points)
        .filter(Points.id == pid)
        .options(joinedload(Points.entity), selectinload(Points.signal_automations))
    )
    result = await dbsession.execute(query)
    points = result.scalar()
    if points is not None:
        return points
    else:
        raise HTTPException(404)


class PatchPointsModel(BaseModel):
    """Model for validating an updated Points."""

    diverge_state: str
    through_state: str


@router.put("/{pid}", response_model=PointsModel)
async def put_points(pid: int, data: PatchPointsModel, dbsession=Depends(inject_db_session)) -> Points:
    """Update a single set of points."""
    query = (
        select(Points)
        .filter(Points.id == pid)
        .options(joinedload(Points.entity), selectinload(Points.signal_automations))
    )
    result = await dbsession.execute(query)
    points = result.scalar()
    if points is not None:
        points.diverge_state = data.diverge_state
        points.through_state = data.through_state
        await dbsession.commit()
        await dbsession.refresh(points)
        await recalculate_state()
        return points
    else:
        raise HTTPException(404)


@router.delete("/{pid}", status_code=204)
async def delete_points(pid: int, dbsession=Depends(inject_db_session)) -> None:
    """Delete a single set of points."""
    query = (
        select(Points)
        .filter(Points.id == pid)
        .options(joinedload(Points.entity), selectinload(Points.signal_automations))
    )
    result = await dbsession.execute(query)
    points = result.scalar()
    if points is not None:
        await dbsession.delete(points)
        await dbsession.commit()
    else:
        raise HTTPException(404)
