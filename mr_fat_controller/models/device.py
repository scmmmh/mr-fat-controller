# SPDX-FileCopyrightText: 2023-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""Models for a single device."""

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from sqlalchemy import Column, DateTime, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson

from mr_fat_controller.models.meta import Base
from mr_fat_controller.models.util import datetime_to_timestamp, objects_to_model_ids
from mr_fat_controller.util import is_recently_active as check_recently_active


class Device(Base):
    """The Device database model."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    external_id = Column(Unicode(255), unique=True)
    name = Column(Unicode(255))
    last_seen = Column(DateTime)
    attrs = Column(NestedMutableJson)

    entities = relationship("Entity", back_populates="device", cascade="all, delete-orphan")


class DeviceModel(BaseModel):
    """Model for returning a Device."""

    id: int
    external_id: str
    name: str
    last_seen: Annotated[int, BeforeValidator(datetime_to_timestamp)]
    is_recently_active: Annotated[bool, BeforeValidator(check_recently_active)] = Field(validation_alias="last_seen")
    attrs: dict

    entities: Annotated[list[int], BeforeValidator(objects_to_model_ids)]

    model_config = ConfigDict(from_attributes=True)
