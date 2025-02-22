# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for signals."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from mr_fat_controller.models import Signal, SignalModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/signals")


class CreateSignalModel(BaseModel):
    """Model for validating a new signals."""

    entity_id: int


@router.post("", response_model=SignalModel)
async def create_signal(data: CreateSignalModel, dbsession=Depends(inject_db_session)) -> Signal:
    """Create new signal."""
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
    """Get all signals."""
    query = (
        select(Signal).order_by(Signal.id).options(joinedload(Signal.entity), selectinload(Signal.signal_automations))
    )
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{sid}", response_model=SignalModel)
async def get_signal(sid: int, dbsession=Depends(inject_db_session)) -> Signal:
    """Get a signal."""
    query = (
        select(Signal)
        .filter(Signal.id == sid)
        .options(joinedload(Signal.entity), selectinload(Signal.signal_automations))
    )
    signal = (await dbsession.execute(query)).scalar()
    if signal is not None:
        return signal
    else:
        raise HTTPException(404, "No such signal found")


@router.delete("/{sid}", status_code=204)
async def delete_signal(sid: int, dbsession=Depends(inject_db_session)) -> None:
    """Delete a signal."""
    query = (
        select(Signal)
        .filter(Signal.id == sid)
        .options(joinedload(Signal.entity), selectinload(Signal.signal_automations))
    )
    signal = (await dbsession.execute(query)).scalar()
    if signal is not None:
        await dbsession.delete(signal)
        await dbsession.commit()
        await recalculate_state()
        await full_state_refresh()
    else:
        raise HTTPException(404, "No such signal found")
