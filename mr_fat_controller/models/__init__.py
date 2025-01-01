"""Functionality for database access."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from threading import local  # pyright: ignore[reportAttributeAccessIssue]
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from mr_fat_controller.models.device import Device  # noqa: F401
from mr_fat_controller.models.entity import Entity, EntityModel  # noqa: F401
from mr_fat_controller.models.meta import Base, MetaData  # noqa: F401
from mr_fat_controller.models.points import Points, PointsModel  # noqa: F401
from mr_fat_controller.models.power_switch import PowerSwitch, PowerSwitchModel  # noqa: F401
from mr_fat_controller.settings import settings

logger = logging.getLogger(__name__)
local_cache = local()


def get_engine() -> AsyncEngine:
    """Get a thread-local engine."""
    try:
        return local_cache.engine
    except Exception:
        local_cache.engine = create_async_engine(settings.dsn)
        return local_cache.engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get a thread-local session factory."""
    try:
        return local_cache.session_factory
    except Exception:
        local_cache.session_factory = async_sessionmaker(bind=get_engine(), expire_on_commit=False)
        return local_cache.session_factory


async def inject_db_session() -> AsyncGenerator[AsyncSession, Any]:
    """Generate a database session."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        await db.close()


@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession, Any]:
    """Context manager db session."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        await db.close()
