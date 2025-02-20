# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for signals."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select

from mr_fat_controller.models import Signal, SignalModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/signals")


class CreateSignalModel(BaseModel):
    """Model for validating a new Signals."""

    entity_id: int


@router.post("", response_model=SignalModel)
async def create_signal(data: CreateSignalModel, dbsession=Depends(inject_db_session)) -> Signal:
    """Create new Signal."""
    signal = Signal(
        entity_id=data.entity_id,
    )
    dbsession.add(signal)
    await dbsession.commit()
    await recalculate_state()
    await full_state_refresh()
    return signal


@router.get("", response_model=list[SignalModel])
async def get_signals(dbsession=Depends(inject_db_session)) -> list[Signal]:
    """Get all Signals."""
    query = select(Signal).order_by(Signal.id)
    result = await dbsession.execute(query)
    return list(result.scalars())
