"""The Controller database model."""
from pydantic import AnyHttpUrl, BaseModel, ConfigDict
from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from mr_fat_controller.models.meta import Base


class Controller(Base):
    """Model representing an external controller.

    Attributes:
    * id - The unique database id
    """

    __tablename__ = "controllers"

    id = Column(Unicode(64), primary_key=True)  # noqa: A003
    baseurl = Column(Unicode(255))
    name = Column(Unicode(255))
    status = Column(Unicode(255))

    turnouts = relationship("Turnout", back_populates="controller")


class ControllerModel(BaseModel):
    """The Pydantic Controller Model for validating responses."""

    id: str  # noqa: A003
    baseurl: AnyHttpUrl
    name: str
    status: str

    model_config = ConfigDict(from_attributes=True)
