# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single train."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import object_to_model_id


class Train(Base):
    """The Train database model."""

    __tablename__ = "trains"

    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"))

    entity = relationship("Entity", back_populates="train")


class TrainModel(BaseModel):
    """Model for returning a Train."""

    id: int

    entity: Annotated[int, BeforeValidator(object_to_model_id)]

    model_config = ConfigDict(from_attributes=True)
