"""API endpoints for handling points."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

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
    await recalculate_state(dbsession)
    await full_state_refresh()
    return points


@router.get("", response_model=list[PointsModel])
async def get_points(dbsession=Depends(inject_db_session)) -> list[Points]:
    """Return all points."""
    query = (
        select(Points)
        .order_by(Points.id)
        .options(joinedload(Points.diverge_signal), joinedload(Points.root_signal), joinedload(Points.through_signal))
    )
    result = await dbsession.execute(query)
    return list(result.scalars())
