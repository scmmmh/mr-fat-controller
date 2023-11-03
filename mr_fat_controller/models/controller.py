"""The Controller database model."""
from pydantic import BaseModel, AnyHttpUrl
from sqlalchemy import Column, Unicode

from .meta import Base


class Controller(Base):
    """Model representing an external controller.

    Attributes:
    * id - The unique database id
    """

    __tablename__ = 'controllers'

    id = Column(Unicode(64), primary_key=True)
    baseurl = Column(Unicode(255))
    name = Column(Unicode(255))
    status = Column(Unicode(255))


class ControllerModel(BaseModel):
    """The Pydantic Controller Model for validating responses."""

    id: str
    baseurl: AnyHttpUrl
    name: str
    status: str

    class Config:
        """Configuration to enable orm_mode."""

        from_attributes = True
