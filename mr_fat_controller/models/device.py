"""Models for a single device."""

from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from mr_fat_controller.models.meta import Base


class Device(Base):
    """The Device database model."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    external_id = Column(Unicode(255), unique=True)
    name = Column(Unicode(255))
    attrs = Column(NestedMutableJson)

    entities = relationship("Entity")
