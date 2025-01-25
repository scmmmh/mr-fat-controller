from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mr_fat_controller.models import Device, DeviceModel, inject_db_session

router = APIRouter(prefix="/devices")


@router.get("", response_model=list[DeviceModel])
async def get_devices(dbsession=Depends(inject_db_session)) -> list[Device]:
    query = select(Device).options(selectinload(Device.entities))
    result = await dbsession.execute(query)
    return list(result.scalars())


@router.delete("/{did}", status_code=204)
async def delete_device(did: int, dbsession=Depends(inject_db_session)) -> None:
    query = select(Device).filter(Device.id == did)
    result = await dbsession.execute(query)
    entity = result.scalar()
    if entity:
        await dbsession.delete(entity)
        await dbsession.commit()
    else:
        raise HTTPException(404)
