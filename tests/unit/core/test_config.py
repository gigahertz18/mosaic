"""Unit tests for app.core.config."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import (
    DatabaseSettings,
    Environment,
    MissingEnvironmentVariableError,
    Settings,
    load_settings,
)


def test_database_settings_builds_async_dsn(database_settings: DatabaseSettings) -> None:
    assert database_settings.async_dsn == ("postgresql+asyncpg://mosaic_test:mosaic_test@localhost:5432/mosaic_test")


def test_database_settings_builds_sync_dsn(database_settings: DatabaseSettings) -> None:
    assert database_settings.sync_dsn == ("postgresql+psycopg://mosaic_test:mosaic_test@localhost:5432/mosaic_test")


def test_settings_is_local_for_local_environment(test_settings: Settings) -> None:
    local_settings = test_settings.model_copy(update={"environment": Environment.LOCAL})
    assert local_settings.is_local is True
    assert local_settings.is_production is False


def test_settings_is_production_for_production_environment(test_settings: Settings) -> None:
    prod_settings = test_settings.model_copy(update={"environment": Environment.PRODUCTION})
    assert prod_settings.is_production is True
    assert prod_settings.is_local is False


def test_settings_is_frozen_and_hashable(test_settings: Settings) -> None:
    with pytest.raises(ValidationError):
        test_settings.debug = False  # type: ignore[misc]

    assert hash(test_settings) == hash(test_settings)


def test_load_settings_raises_when_required_variable_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOSAIC_DB_HOST", raising=False)

    with pytest.raises(MissingEnvironmentVariableError) as exc_info:
        load_settings()

    assert exc_info.value.name == "MOSAIC_DB_HOST"


def test_load_settings_builds_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOSAIC_ENVIRONMENT", "test")
    monkeypatch.setenv("MOSAIC_DB_HOST", "db")
    monkeypatch.setenv("MOSAIC_DB_USER", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_PASSWORD", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_NAME", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_ENDPOINT", "minio:9000")
    monkeypatch.setenv("MOSAIC_STORAGE_ACCESS_KEY", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_SECRET_KEY", "mosaic123")

    settings = load_settings()

    assert settings.environment == Environment.TEST
    assert settings.database.host == "db"
    assert settings.storage.endpoint == "minio:9000"


def test_load_settings_never_reads_dotenv_file() -> None:
    """Guard against regressions: this module must not import python-dotenv."""
    import app.core.config as config_module

    assert "dotenv" not in dir(config_module)
