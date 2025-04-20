# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for power switches."""

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from mr_fat_controller.models import PowerSwitch, PowerSwitchModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/power-switches")


class CreatePowerSwitchModel(BaseModel):
    """Model for validating a new PowerSwitches."""

    entity_id: int


@router.post("", response_model=PowerSwitchModel)
async def create_power_switch(data: CreatePowerSwitchModel, dbsession=Depends(inject_db_session)) -> PowerSwitch:
    """Create a new power switch."""
    power_switch = PowerSwitch(
        entity_id=data.entity_id,
    )
    dbsession.add(power_switch)
    await dbsession.commit()
    await recalculate_state()
    await full_state_refresh()
    return await get_power_switch(power_switch.id, dbsession=dbsession)  # pyright: ignore [reportArgumentType]


@router.get("", response_model=list[PowerSwitchModel])
async def get_power_switches(dbsession=Depends(inject_db_session)) -> list[PowerSwitch]:
    """GET all power switches."""
    query = select(PowerSwitch).order_by(PowerSwitch.id).options(joinedload(PowerSwitch.entity))
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.get("/{psid}", response_model=PowerSwitchModel)
async def get_power_switch(psid: int, dbsession=Depends(inject_db_session)) -> PowerSwitch:
    """Get a power switch."""
    query = select(PowerSwitch).filter(PowerSwitch.id == psid).options(joinedload(PowerSwitch.entity))
    power_switch = (await dbsession.execute(query)).scalar()
    if power_switch is not None:
        return power_switch
    else:
        raise HTTPException(404, "No such power switch found")


@router.delete("/{psid}", status_code=204)
async def delete_power_switches(psid: int, dbsession=Depends(inject_db_session)) -> None:
    """GET all power switches."""
    query = select(PowerSwitch).filter(PowerSwitch.id == psid).options(joinedload(PowerSwitch.entity))
    power_switch = (await dbsession.execute(query)).scalar()
    if power_switch is not None:
        await dbsession.delete(power_switch)
        await dbsession.commit()
        await recalculate_state()
        await full_state_refresh()
    else:
        raise HTTPException(404, "No such power switch found")
