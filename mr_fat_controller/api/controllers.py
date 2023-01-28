"""Controller manipulation routes."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import db_session, Controller, ControllerModel


router = APIRouter(prefix='/controllers')


@router.get('/', response_model=list[ControllerModel])
async def get_controllers(dbsession: AsyncSession = Depends(db_session)) -> list[Controller]:
    """Return all controllers."""
    query = select(Controller)
    result = await dbsession.execute(query)
    return list(result.scalars())


class CreateControllerModel(BaseModel):
    """The validation model for creating controllers."""

    id: str
    baseurl: str


@router.post('/', response_model=ControllerModel)
async def post_controllers(params: CreateControllerModel, dbsession: AsyncSession = Depends(db_session)) -> Controller:
    """Create a new controller."""
    controller = Controller(id=params.id,
                            baseurl=params.baseurl,
                            name='New controller',
                            status='unknown')
    dbsession.add(controller)
    await dbsession.commit()
    return controller
