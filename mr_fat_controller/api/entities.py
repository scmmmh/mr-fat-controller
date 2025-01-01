from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import Entity, EntityModel, inject_db_session

router = APIRouter(prefix="/entities")


@router.get("", response_model=list[EntityModel])
async def get_entities(dbsession=Depends(inject_db_session)) -> list[Entity]:
    query = select(Entity).order_by(Entity.name).options(selectinload(Entity.points), selectinload(Entity.power_switch))
    result = await dbsession.execute(query)
    return list(result.scalars())
