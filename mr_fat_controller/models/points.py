# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single set of points."""

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base


class Points(Base):
    """The Points database model."""

    __tablename__ = "points"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))
    through_state = Column(Unicode(255))
    diverge_state = Column(Unicode(255))

    entity = relationship("Entity", back_populates="points")


class PointsModel(BaseModel):
    """Model for returning a Points."""

    id: int
    entity_id: int
    through_state: str
    diverge_state: str

    model_config = ConfigDict(from_attributes=True)
