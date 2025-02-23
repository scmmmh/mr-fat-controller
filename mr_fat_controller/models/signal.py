# noqa: A005
# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single entity."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import object_to_model_id, objects_to_model_ids


class Signal(Base):
    """The Signal database model."""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))

    entity = relationship("Entity", back_populates="signal")
    signal_automations = relationship("SignalAutomation", back_populates="signal", cascade="all, delete-orphan")


class SignalModel(BaseModel):
    """Model for returning a Signal."""

    id: int
    entity_id: int

    entity: Annotated[int, BeforeValidator(object_to_model_id)]
    signal_automations: Annotated[list[int], BeforeValidator(objects_to_model_ids)]

    model_config = ConfigDict(from_attributes=True)
