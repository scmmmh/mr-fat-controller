# noqa: A005
# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single entity."""

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
