"""Models for a single entity."""  # noqa: A005

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base


class Signal(Base):
    """The Signal database model."""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))

    entity = relationship("Entity", back_populates="signal")


class SignalModel(BaseModel):
    """Model for returning a Signal."""

    id: int
    entity_id: int

    model_config = ConfigDict(from_attributes=True)
