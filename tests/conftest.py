"""Shared pytest fixtures.

Per project convention, tests never rely on environment variables or a
``.env`` file — configuration objects are constructed explicitly here.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from app.core.config import (
    DatabaseSettings,
    Environment,
    LoggingSettings,
    ObjectStorageSettings,
    Settings,
)


@pytest.fixture
def database_settings() -> DatabaseSettings:
    return DatabaseSettings(
        host="localhost",
        port=5432,
        user="mosaic_test",
        password="mosaic_test",
        name="mosaic_test",
    )


@pytest.fixture
def storage_settings() -> ObjectStorageSettings:
    return ObjectStorageSettings(
        endpoint="localhost:9000",
        access_key="mosaic_test",
        secret_key="mosaic_test",
        bucket="mosaic-test",
        secure=False,
    )


@pytest.fixture
def test_settings(database_settings: DatabaseSettings, storage_settings: ObjectStorageSettings) -> Settings:
    return Settings(
        environment=Environment.TEST,
        debug=True,
        database=database_settings,
        storage=storage_settings,
        logging=LoggingSettings(level="DEBUG", json_format=False),
    )


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    """Ensure ``get_settings``'s lru_cache never leaks state between tests."""
    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
