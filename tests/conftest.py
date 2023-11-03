"""Test fixtures."""
import asyncio

import pytest

from mr_fat_controller.cli import execute_setup


@pytest.fixture()
def empty_database() -> None:
    """Ensure the database is empty and ready."""
    asyncio.run(execute_setup(drop_existing=True))
