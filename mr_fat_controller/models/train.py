# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single train."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import object_to_model_id, objects_to_model_ids


class Train(Base):
    """The Train database model."""

    __tablename__ = "trains"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))
    max_speed = Column(Integer)
    max_acceleration = Column(Float)
    max_deceleration = Column(Float)
    aerodynamic_resistance = Column(Float)

    entity = relationship("Entity", back_populates="train")
    controllers = relationship("TrainController", back_populates="train")


class TrainModel(BaseModel):
    """Model for returning a Train."""

    id: int
    entity: Annotated[int, BeforeValidator(object_to_model_id)]
    max_speed: int
    max_acceleration: float
    max_deceleration: float
    aerodynamic_resistance: float
    controllers: Annotated[list[int], BeforeValidator(objects_to_model_ids)]

    model_config = ConfigDict(from_attributes=True)
