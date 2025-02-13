# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for signals."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import Entity, Train, TrainModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/trains")


class CreateTrainModel(BaseModel):
    """Model for validating a new train."""

    entity_id: int
    name: str


@router.post("", response_model=TrainModel)
async def create_train(data: CreateTrainModel, dbsession=Depends(inject_db_session)) -> Train:
    """Create new train."""
    query = select(Entity).filter(Entity.id == data.entity_id).options(selectinload(Entity.train))
    entity = (await dbsession.execute(query)).scalar()
    if entity:
        train = Train(name=data.name)
        train.entities.append(entity)
        dbsession.add(train)
        await dbsession.commit()
        await recalculate_state()
        await full_state_refresh()
        return train
    else:
        raise HTTPException(422, "Entity not set or found")


@router.get("", response_model=list[TrainModel])
async def get_trains(dbsession=Depends(inject_db_session)) -> list[Train]:
    """Get all trains."""
    query = select(Train).order_by(Train.id).options(selectinload(Train.entities))
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{tid}", response_model=TrainModel)
async def get_train(tid: int, dbsession=Depends(inject_db_session)) -> Train:
    """Get a train."""
    query = select(Train).filter(Train.id == tid).options(selectinload(Train.entities))
    train = (await dbsession.execute(query)).scalar()
    if train is not None:
        return train
    else:
        raise HTTPException(404, "No such train found")


class PatchTrainModel(BaseModel):
    """Model for validating patching a train."""

    entity_id: int | None = None


@router.patch("/{tid}", response_model=TrainModel)
async def patch_train(tid: int, data: PatchTrainModel, dbsession=Depends(inject_db_session)) -> Train:
    """Patch a train."""
    query = select(Train).filter(Train.id == tid).options(selectinload(Train.entities))
    train = (await dbsession.execute(query)).scalar()
    if train:
        query = select(Entity).filter(Entity.id == data.entity_id).options(selectinload(Entity.train))
        entity = (await dbsession.execute(query)).scalar()
        if entity:
            train.entities.append(entity)
            await dbsession.commit()
            await dbsession.refresh(train)
            await recalculate_state()
            await full_state_refresh()
            return train
        else:
            raise HTTPException(422, "Entity not set or found")
    else:
        raise HTTPException(404, "No such train found")
