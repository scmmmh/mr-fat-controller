# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single train controller."""

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import object_to_model_id


class TrainController(Base):
    """The TrainController database model."""

    __tablename__ = "train_controllers"

    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey("trains.id"))
    name = Column(Unicode(255))
    mode = Column(Unicode(255))

    train = relationship("Train", back_populates="controllers")


class TrainControllerModel(BaseModel):
    """Model for returning a TrainController."""

    id: int
    train: Annotated[int, BeforeValidator(object_to_model_id)]
    name: str
    mode: Literal["direct"] | Literal["combined"] | Literal["separate"]

    model_config = ConfigDict(from_attributes=True)
