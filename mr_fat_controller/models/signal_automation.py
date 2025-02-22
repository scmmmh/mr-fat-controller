# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for the signal automation."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import object_to_model_id


class SignalAutomation(Base):
    """The signal automation database model."""

    __tablename__ = "signal_automations"

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals.id"))
    block_detector_id = Column(Integer, ForeignKey("block_detectors.id"))
    points_id = Column(Integer, ForeignKey("points.id"), nullable=True)
    points_state = Column(Unicode(255))

    signal = relationship("Signal", back_populates="signal_automations")
    block_detector = relationship("BlockDetector", back_populates="signal_automations")
    points = relationship("Points", back_populates="signal_automations")


class SignalAutomationModel(BaseModel):
    """Model for returning a SignalAutomation."""

    id: int
    points_state: str

    signal: Annotated[int, BeforeValidator(object_to_model_id)]
    block_detector: Annotated[int, BeforeValidator(object_to_model_id)]
    points: Annotated[int | None, BeforeValidator(object_to_model_id)]

    model_config = ConfigDict(from_attributes=True)
