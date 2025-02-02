# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for handling entities."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import Entity, EntityModel, inject_db_session

router = APIRouter(prefix="/entities")


@router.get("", response_model=list[EntityModel])
async def get_entities(dbsession=Depends(inject_db_session)) -> list[Entity]:
    """GET all entities."""
    query = (
        select(Entity)
        .order_by(Entity.device_class, Entity.name)
        .options(
            selectinload(Entity.block_detector),
            selectinload(Entity.device),
            selectinload(Entity.points),
            selectinload(Entity.power_switch),
            selectinload(Entity.signal),
        )
    )
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.delete("/{eid}", status_code=204)
async def delete_entity(eid: int, dbsession=Depends(inject_db_session)) -> None:
    """Delete a single `Entity`."""
    query = select(Entity).filter(Entity.id == eid)
    result = await dbsession.execute(query)
    entity = result.scalar()
    if entity:
        await dbsession.delete(entity)
        await dbsession.commit()
    else:
        raise HTTPException(404)
