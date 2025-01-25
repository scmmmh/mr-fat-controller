"""Models for a single entity."""

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base


class PowerSwitch(Base):
    """The PointSwitch database model."""

    __tablename__ = "power_switches"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))

    entity = relationship("Entity", back_populates="power_switch")


class PowerSwitchModel(BaseModel):
    """Model for returning a PowerSwitch."""

    id: int
    entity_id: int

    model_config = ConfigDict(from_attributes=True)
