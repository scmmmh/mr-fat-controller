# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single set of points."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import object_to_model_id, objects_to_model_ids


class Points(Base):
    """The Points database model."""

    __tablename__ = "points"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))
    through_state = Column(Unicode(255))
    diverge_state = Column(Unicode(255))

    entity = relationship("Entity", back_populates="points")
    signal_automations = relationship("SignalAutomation", back_populates="points", cascade="all, delete-orphan")


class PointsModel(BaseModel):
    """Model for returning a Points."""

    id: int
    entity_id: int
    through_state: str
    diverge_state: str

    entity: Annotated[int, BeforeValidator(object_to_model_id)]
    signal_automations: Annotated[list[int], BeforeValidator(objects_to_model_ids)]

    model_config = ConfigDict(from_attributes=True)
