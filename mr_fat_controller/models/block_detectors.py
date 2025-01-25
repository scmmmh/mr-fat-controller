"""Models for a single entity."""

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base


class BlockDetector(Base):
    """The BlockDetector database model."""

    __tablename__ = "block_detectors"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))

    entity = relationship("Entity", back_populates="block_detector")


class BlockDetectorModel(BaseModel):
    """Model for returning a BlockDetector."""

    id: int
    entity_id: int

    model_config = ConfigDict(from_attributes=True)
