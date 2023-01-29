"""Controller manipulation routes."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, AnyHttpUrl, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..models import db_session, Controller, ControllerModel


logger = logging.getLogger(__name__)
router = APIRouter(prefix='/controllers')


@router.get('/', response_model=list[ControllerModel])
async def get_controllers(dbsession: AsyncSession = Depends(db_session)) -> list[Controller]:
    """Return all controllers."""
    query = select(Controller)
    result = await dbsession.execute(query)
    return list(result.scalars())


class CreateControllerModel(BaseModel):
    """The validation model for creating controllers."""

    id: str = Field(min_length=1)
    baseurl: AnyHttpUrl


@router.post('/', response_model=ControllerModel)
async def post_controllers(params: CreateControllerModel, dbsession: AsyncSession = Depends(db_session)) -> Controller:
    """Create a new controller."""
    controller = Controller(id=params.id,
                            baseurl=params.baseurl,
                            name='New controller',
                            status='unknown')
    dbsession.add(controller)
    try:
        await dbsession.commit()
        return controller
    except IntegrityError as e:
        logger.error(e)
        raise HTTPException(409, 'The given id is already in use.')


@router.get('/{id}', response_model=ControllerModel)
async def get_controller(id: str, dbsession: AsyncSession = Depends(db_session)) -> Controller:
    """Fetch a specific controller."""
    query = select(Controller).filter(Controller.id == id)
    result = await dbsession.execute(query)
    controller = result.scalar()
    if controller is None:
        raise HTTPException(404, 'No controller exists with this id.')
    else:
        return controller


class PutControllerModel(BaseModel):
    """Model for validating controller updates."""

    baseurl: Optional[AnyHttpUrl]
    name: Optional[str] = Field(min_length=1)


@router.put('/{id}', response_model=ControllerModel)
async def put_controller(id: str, params: PutControllerModel, dbsession: AsyncSession = Depends(db_session)) -> Controller:  # noqa: E501
    """Fetch a specific controller."""
    query = select(Controller).filter(Controller.id == id)
    result = await dbsession.execute(query)
    controller = result.scalar()
    if controller is None:
        raise HTTPException(404, 'No controller exists with this id.')
    else:
        if params.baseurl is not None:
            controller.baseurl = params.baseurl
        if params.name is not None:
            controller.name = params.name
        await dbsession.commit()
        return controller


@router.delete('/{id}', status_code=204)
async def delete_controller(id: str, dbsession: AsyncSession = Depends(db_session)) -> None:
    """Delete a specific controller."""
    query = select(Controller).filter(Controller.id == id)
    result = await dbsession.execute(query)
    controller = result.scalar()
    if controller is None:
        raise HTTPException(404, 'No controller exists with this id.')
    else:
        await dbsession.delete(controller)
        await dbsession.commit()
