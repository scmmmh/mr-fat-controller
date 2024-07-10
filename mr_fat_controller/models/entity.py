"""Models for a single entity."""

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from mr_fat_controller.models.meta import Base


class Entity(Base):
    """The Entity database model."""

    __tablename__ = "entities"

    id = Column(Integer, primary_key=True)
    external_id = Column(Unicode(255), unique=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    name = Column(Unicode(255))
    device_class = Column(Unicode(255))
    state_topic = Column(Unicode(255), unique=True)
    command_topic = Column(Unicode(255), unique=True)
    attrs = Column(NestedMutableJson)

    device = relationship("Device", back_populates="entities")
    points = relationship("Points", back_populates="entity")


class EntityModel(BaseModel):
    """Model for returning an Entity."""

    id: int
    external_id: str
    device_id: int
    name: str
    device_class: str
    state_topic: str
    command_topic: str
    attrs: dict

    model_config = ConfigDict(from_attributes=True)
