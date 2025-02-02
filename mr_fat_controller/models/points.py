# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single set of points."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import object_to_model_id


class Points(Base):
    """The Points database model."""

    __tablename__ = "points"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))
    through_state = Column(Unicode(255))
    diverge_state = Column(Unicode(255))
    through_signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)
    diverge_signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)
    root_signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)

    entity = relationship("Entity", back_populates="points")
    through_signal = relationship("Signal", foreign_keys="Points.through_signal_id")
    diverge_signal = relationship("Signal", foreign_keys="Points.diverge_signal_id")
    root_signal = relationship("Signal", foreign_keys="Points.root_signal_id")


class PointsModel(BaseModel):
    """Model for returning a Points."""

    id: int
    entity_id: int
    through_state: str
    diverge_state: str
    diverge_signal: Annotated[int | None, BeforeValidator(object_to_model_id)]
    root_signal: Annotated[int | None, BeforeValidator(object_to_model_id)]
    through_signal: Annotated[int | None, BeforeValidator(object_to_model_id)]

    model_config = ConfigDict(from_attributes=True)
