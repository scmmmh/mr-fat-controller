"""Models for a single device."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import objects_to_model_ids


class Device(Base):
    """The Device database model."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    external_id = Column(Unicode(255), unique=True)
    name = Column(Unicode(255))
    attrs = Column(NestedMutableJson)

    entities = relationship("Entity", back_populates="device", cascade="all, delete-orphan")


class DeviceModel(BaseModel):
    """Model for returning a Device"""

    id: int
    external_id: str
    name: str
    attrs: dict

    entities: Annotated[list[int], BeforeValidator(objects_to_model_ids)]

    model_config = ConfigDict(from_attributes=True)
