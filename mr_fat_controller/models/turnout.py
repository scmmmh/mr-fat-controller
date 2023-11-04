"""The Controller database model."""
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Unicode, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson
from typing import Literal

from mr_fat_controller.models.meta import Base


class Turnout(Base):
    """Model representing a turnout.

    Attributes:
    * id - The unique database id
    * controller_id - The unique id of the controller the turnout is controlled by
    * name - The display name for this turnout
    * status - The current turnout status
    * parameters - The hardware configuration parameters
    """

    __tablename__ = "turnouts"

    id = Column(Unicode(64), primary_key=True)  # noqa: A003
    controller_id = Column(Unicode(64), ForeignKey("controllers.id"))  # noqa: A003
    name = Column(Unicode(255))
    state = Column(Unicode(255))
    parameters = Column(NestedMutableJson)

    controller = relationship("Controller", back_populates="turnouts")


class TurnoutTwoPinSolenoidParametersModel(BaseModel):
    """The Pydantic model for validating TwoPinSolenoidTurnouts."""

    type: Literal["TwoPinSolenoidTurnout"]
    enable_pin: int
    direction_pin: int
    turnout_high: bool


class TurnoutModel(BaseModel):
    """The Pydantic Turnout Model for validating responses."""

    id: str  # noqa: A003
    controller_id: str
    name: str
    state: str
    parameters: TurnoutTwoPinSolenoidParametersModel

    model_config = ConfigDict(from_attributes=True)
