"""Functionality for database access."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .meta import MetaData, Base  # noqa
from .controller import Controller, ControllerModel  # noqa
from ..settings import settings

logger = logging.getLogger(__name__)
engine = create_async_engine(settings['dsn'])
session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def db_session() -> AsyncSession:
    """Get a database session."""
    db = session_factory()
    try:
        yield db
    finally:
        await db.close()
