"""Models for a single entity."""

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
