# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for signal automations."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from mr_fat_controller.models import SignalAutomation, SignalAutomationModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/signal-automations")


class CreateSignalAutomationModel(BaseModel):
    """Model for validating a new SignalAutomation."""

    signal: int
    name: str
    block_detector: int
    points: int | None
    points_state: str


@router.post("", response_model=SignalAutomationModel)
async def create_signal_automation(
    data: CreateSignalAutomationModel, dbsession=Depends(inject_db_session)
) -> SignalAutomation:
    """Create new SignalAutomation."""
    signal_automation = SignalAutomation(
        name=data.name,
        signal_id=data.signal,
        block_detector_id=data.block_detector,
        points_id=data.points,
        points_state=data.points_state,
    )
    dbsession.add(signal_automation)
    await dbsession.commit()
    await recalculate_state()
    await full_state_refresh()
    query = (
        select(SignalAutomation)
        .filter(SignalAutomation.id == signal_automation.id)
        .options(
            joinedload(SignalAutomation.signal),
            joinedload(SignalAutomation.block_detector),
            joinedload(SignalAutomation.points),
        )
    )
    signal_automation = (await dbsession.execute(query)).scalar()
    return signal_automation


@router.get("", response_model=list[SignalAutomationModel])
async def get_signal_automations(dbsession=Depends(inject_db_session)) -> list[SignalAutomation]:
    """Get all SignalAutomations."""
    query = (
        select(SignalAutomation)
        .order_by(SignalAutomation.id)
        .options(
            joinedload(SignalAutomation.signal),
            joinedload(SignalAutomation.block_detector),
            joinedload(SignalAutomation.points),
        )
    )
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{sid}", response_model=SignalAutomationModel)
async def get_signal_automation(sid: int, dbsession=Depends(inject_db_session)) -> SignalAutomation:
    """Get a SignalAutomation."""
    query = (
        select(SignalAutomation)
        .filter(SignalAutomation.id == sid)
        .options(
            joinedload(SignalAutomation.signal),
            joinedload(SignalAutomation.block_detector),
            joinedload(SignalAutomation.points),
        )
    )
    signal_automation = (await dbsession.execute(query)).scalar()
    if signal_automation is not None:
        return signal_automation
    else:
        raise HTTPException(404, "No such SignalAutomation found")


class UpdateSignalAutomationModel(BaseModel):
    """Model for validating an update to a SignalAutomation."""

    id: int
    signal: int
    name: str
    block_detector: int
    points: int | None
    points_state: str


@router.put("/{sid}", response_model=SignalAutomationModel)
async def update_signal_automation(
    sid: int, data: UpdateSignalAutomationModel, dbsession=Depends(inject_db_session)
) -> SignalAutomation:
    """Update a SignalAutomation."""
    query = (
        select(SignalAutomation)
        .filter(SignalAutomation.id == sid)
        .options(
            joinedload(SignalAutomation.signal),
            joinedload(SignalAutomation.block_detector),
            joinedload(SignalAutomation.points),
        )
    )
    signal_automation = (await dbsession.execute(query)).scalar()
    if signal_automation is not None:
        signal_automation.name = data.name
        signal_automation.signal_id = data.signal
        signal_automation.block_detector_id = data.block_detector
        signal_automation.points_id = data.points
        signal_automation.points_state = data.points_state
        await dbsession.commit()
        await dbsession.refresh(signal_automation)
        await recalculate_state()
        await full_state_refresh()
        return signal_automation
    else:
        raise HTTPException(404, "No such SignalAutomation found")


@router.delete("/{sid}", status_code=204)
async def delete_signal_automation(sid: int, dbsession=Depends(inject_db_session)) -> None:
    """Delete a SignalAutomation."""
    query = (
        select(SignalAutomation)
        .filter(SignalAutomation.id == sid)
        .options(
            joinedload(SignalAutomation.signal),
            joinedload(SignalAutomation.block_detector),
            joinedload(SignalAutomation.points),
        )
    )
    signal_automation = (await dbsession.execute(query)).scalar()
    if signal_automation is not None:
        await dbsession.delete(signal_automation)
        await dbsession.commit()
        await recalculate_state()
        await full_state_refresh()
    else:
        raise HTTPException(404, "No such SignalAutomation found")
