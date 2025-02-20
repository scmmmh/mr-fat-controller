# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""API endpoints for power switches."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select

from mr_fat_controller.models import PowerSwitch, PowerSwitchModel, inject_db_session
from mr_fat_controller.mqtt import full_state_refresh, recalculate_state

router = APIRouter(prefix="/power-switches")


class CreatePowerSwitchModel(BaseModel):
    """Model for validating a new PowerSwitches."""

    entity_id: int


@router.post("", response_model=PowerSwitchModel)
async def create_points(data: CreatePowerSwitchModel, dbsession=Depends(inject_db_session)) -> PowerSwitch:
    """Create a new power switch."""
    power_switch = PowerSwitch(
        entity_id=data.entity_id,
    )
    dbsession.add(power_switch)
    await dbsession.commit()
    await recalculate_state()
    await full_state_refresh()
    return power_switch


@router.get("", response_model=list[PowerSwitchModel])
async def get_power_switches(dbsession=Depends(inject_db_session)) -> list[PowerSwitch]:
    """GET all power switches."""
    query = select(PowerSwitch).order_by(PowerSwitch.id)
    result = await dbsession.execute(query)
    return list(result.scalars())
