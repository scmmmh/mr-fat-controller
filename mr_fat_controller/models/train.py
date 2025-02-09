# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single entity."""

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base

entity_trains = Table(
    "entity_trains",
    Base.metadata,
    Column("entity_id", Integer, ForeignKey("entities.id"), primary_key=True, unique=True),
    Column("train_id", Integer, ForeignKey("trains.id"), primary_key=True),
)


class Train(Base):
    """The Train database model."""

    __tablename__ = "trains"

    id = Column(Integer, primary_key=True)

    entities = relationship("Entity", back_populates="train", secondary=entity_trains)


class TrainModel(BaseModel):
    """Model for returning a Train."""

    id: int

    model_config = ConfigDict(from_attributes=True)
