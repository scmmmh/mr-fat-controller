"""Models for a single entity."""

from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict
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
    command_topic = Column(Unicode(255), nullable=True)
    attrs = Column(NestedMutableJson)

    block_detector = relationship("BlockDetector", back_populates="entity", uselist=False)
    device = relationship("Device", back_populates="entities")
    points = relationship("Points", back_populates="entity", uselist=False)
    power_switch = relationship("PowerSwitch", back_populates="entity", uselist=False)


def object_to_model_id(model: Any | None) -> int | None:
    """Return the model id for a model."""
    if model is not None:
        return model.id
    return None


class EntityModel(BaseModel):
    """Model for returning an Entity."""

    id: int
    external_id: str
    device_id: int
    name: str
    device_class: str
    state_topic: str
    command_topic: str | None
    attrs: dict

    block_detector: Annotated[int | None, BeforeValidator(object_to_model_id)]
    points: Annotated[int | None, BeforeValidator(object_to_model_id)]
    power_switch: Annotated[int | None, BeforeValidator(object_to_model_id)]

    model_config = ConfigDict(from_attributes=True)
