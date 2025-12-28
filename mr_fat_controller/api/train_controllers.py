# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for signals."""

from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import TrainController, TrainControllerModel, inject_db_session

router = APIRouter(prefix="/train-controllers")


class CreateTrainControllerModel(BaseModel):
    """Model for validating a new train_controller."""

    train: int
    name: str
    mode: Literal["direct"] | Literal["combined"] | Literal["separate"]


@router.post("", response_model=TrainControllerModel)
async def create_train_controller(
    data: CreateTrainControllerModel, dbsession=Depends(inject_db_session)
) -> TrainController:
    """Create new train controller."""
    train_controller = TrainController(train_id=data.train, name=data.name, mode=data.mode)
    dbsession.add(train_controller)
    await dbsession.commit()
    return await get_train_controller(train_controller.id, dbsession=dbsession)  # pyright: ignore [reportArgumentType]


@router.get("", response_model=list[TrainControllerModel])
async def get_train_controllers(dbsession=Depends(inject_db_session)) -> list[TrainController]:
    """Get all train controllers."""
    query = select(TrainController).order_by(TrainController.name).options(selectinload(TrainController.train))
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{tid}", response_model=TrainControllerModel)
async def get_train_controller(tid: int, dbsession=Depends(inject_db_session)) -> TrainController:
    """Get a train controller."""
    query = select(TrainController).filter(TrainController.id == tid).options(selectinload(TrainController.train))
    train_controller = (await dbsession.execute(query)).scalar()
    if train_controller is not None:
        return train_controller
    else:
        raise HTTPException(404, "No such train controller found")


class UpdateTrainControllerModel(BaseModel):
    """Model to validate updates to a train controller."""

    id: int
    name: str
    mode: Literal["direct"] | Literal["combined"] | Literal["separate"]


@router.put("/{tid}", response_model=TrainControllerModel)
async def update_train_controller(
    tid: int, data: UpdateTrainControllerModel, dbsession=Depends(inject_db_session)
) -> TrainController:
    """Update a train_controller."""
    query = select(TrainController).filter(TrainController.id == tid).options(selectinload(TrainController.train))
    train_controller = (await dbsession.execute(query)).scalar()
    if train_controller is not None:
        train_controller.name = data.name
        train_controller.mode = data.mode
        await dbsession.commit()
        return train_controller
    else:
        raise HTTPException(404, "No such train controller found")


@router.delete("/{tid}", status_code=204)
async def delete_train_controller(tid: int, dbsession=Depends(inject_db_session)) -> None:
    """Delete a train controller."""
    query = select(TrainController).filter(TrainController.id == tid)
    train_controller = (await dbsession.execute(query)).scalar()
    if train_controller is not None:
        await dbsession.delete(train_controller)
        await dbsession.commit()
    else:
        raise HTTPException(404, "No such train controller found")
