# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for signals."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import Train, TrainModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/trains")


class CreateTrainModel(BaseModel):
    """Model for validating a new train."""

    entity_id: int


@router.post("", response_model=TrainModel)
async def create_train(data: CreateTrainModel, dbsession=Depends(inject_db_session)) -> Train:
    """Create new train."""
    train = Train(entity_id=data.entity_id, max_speed=0)
    dbsession.add(train)
    await dbsession.commit()
    await recalculate_state()
    await full_state_refresh()
    return await get_train(train.id, dbsession=dbsession)  # pyright: ignore [reportArgumentType]


@router.get("", response_model=list[TrainModel])
async def get_trains(dbsession=Depends(inject_db_session)) -> list[Train]:
    """Get all trains."""
    query = (
        select(Train).order_by(Train.id).options(selectinload(Train.entity)).options(selectinload(Train.controllers))
    )
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{tid}", response_model=TrainModel)
async def get_train(tid: int, dbsession=Depends(inject_db_session)) -> Train:
    """Get a train."""
    query = (
        select(Train)
        .filter(Train.id == tid)
        .options(selectinload(Train.entity))
        .options(selectinload(Train.controllers))
    )
    train = (await dbsession.execute(query)).scalar()
    if train is not None:
        return train
    else:
        raise HTTPException(404, "No such train found")


class UpdateTrainModel(BaseModel):
    """Model to validate updates to a train."""

    id: int
    entity: int
    max_speed: int


@router.put("/{tid}", response_model=TrainModel)
async def update_train(tid: int, data: UpdateTrainModel, dbsession=Depends(inject_db_session)) -> Train:
    """Update a train."""
    query = (
        select(Train)
        .filter(Train.id == tid)
        .options(selectinload(Train.entity))
        .options(selectinload(Train.controllers))
    )
    train = (await dbsession.execute(query)).scalar()
    if train is not None:
        train.max_speed = data.max_speed
        await dbsession.commit()
        return train
    else:
        raise HTTPException(404, "No such train found")


@router.delete("/{tid}", status_code=204)
async def delete_train(tid: int, dbsession=Depends(inject_db_session)) -> None:
    """Delete a trains."""
    query = select(Train).filter(Train.id == tid)
    train = (await dbsession.execute(query)).scalar()
    if train is not None:
        await dbsession.delete(train)
        await dbsession.commit()
    else:
        raise HTTPException(404, "No such train found")
