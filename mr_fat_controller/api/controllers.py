"""Controller manipulation routes."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AnyHttpUrl, BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mr_fat_controller.models import Controller, ControllerModel, db_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/controllers")


@router.get("/", response_model=list[ControllerModel])
async def get_controllers(dbsession: AsyncSession = Depends(db_session)) -> list[Controller]:
    """Return all controllers."""
    query = select(Controller)
    result = await dbsession.execute(query)
    return list(result.scalars())


class CreateControllerModel(BaseModel):
    """The validation model for creating controllers."""

    id: str = Field(min_length=1)  # noqa: A003
    baseurl: AnyHttpUrl


@router.post("/", response_model=ControllerModel)
async def post_controllers(params: CreateControllerModel, dbsession: AsyncSession = Depends(db_session)) -> Controller:
    """Create a new controller."""
    controller = Controller(id=params.id, baseurl=str(params.baseurl), name="New controller", status="unknown")
    dbsession.add(controller)
    try:
        await dbsession.commit()
        return controller
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(409, "The given id is already in use.") from err


@router.get("/{cid}", response_model=ControllerModel)
async def get_controller(cid: str, dbsession: AsyncSession = Depends(db_session)) -> Controller:
    """Fetch a specific controller."""
    query = select(Controller).filter(Controller.id == cid)
    result = await dbsession.execute(query)
    controller = result.scalar()
    if controller is None:
        raise HTTPException(404, "No controller exists with this id.")
    else:
        return controller


class PutControllerModel(BaseModel):
    """Model for validating controller updates."""

    baseurl: Optional[AnyHttpUrl] = None
    name: Optional[str] = Field(min_length=1, default=None)


@router.patch("/{cid}", response_model=ControllerModel)
async def patch_controller(
    cid: str, params: PutControllerModel, dbsession: AsyncSession = Depends(db_session)
) -> Controller:
    """Fetch a specific controller."""
    query = select(Controller).filter(Controller.id == cid)
    result = await dbsession.execute(query)
    controller = result.scalar()
    if controller is None:
        raise HTTPException(404, "No controller exists with this id.")
    else:
        if params.baseurl is not None:
            controller.baseurl = str(params.baseurl)
        if params.name is not None:
            controller.name = params.name
        await dbsession.commit()
        return controller


@router.delete("/{cid}", status_code=204)
async def delete_controller(cid: str, dbsession: AsyncSession = Depends(db_session)) -> None:
    """Delete a specific controller."""
    query = select(Controller).filter(Controller.id == cid)
    result = await dbsession.execute(query)
    controller = result.scalar()
    if controller is None:
        raise HTTPException(404, "No controller exists with this id.")
    else:
        await dbsession.delete(controller)
        await dbsession.commit()
