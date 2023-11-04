"""Turnout manipulation routes."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal

from mr_fat_controller.models import Turnout, TurnoutModel, db_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/turnouts")


@router.get("/", response_model=list[TurnoutModel])
async def get_turnouts(dbsession: AsyncSession = Depends(db_session)) -> list[Turnout]:
    """Return all turnouts."""
    query = select(Turnout).order_by(Turnout.name)
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.put("/{tid}/{direction}", response_model=TurnoutModel)
async def set_turnout_direction(
    tid: str, direction: Literal["straight"] | Literal["turn"], dbsession: AsyncSession = Depends(db_session)
) -> Turnout:
    """Set the direction of a turnout."""
    query = select(Turnout).filter(Turnout.id == tid).options(selectinload(Turnout.controller))
    turnout = (await dbsession.execute(query)).scalar()
    if turnout:
        async with AsyncClient() as client:
            response = await client.patch(
                f"{turnout.controller.baseurl}api/turnouts/{turnout.id}", json={"state": direction}
            )
            if response.status_code == 200:
                turnout.state = response.json()["state"]
            else:
                turnout.state = "unknown"
        await dbsession.commit()
        return turnout
    else:
        raise HTTPException(404)
